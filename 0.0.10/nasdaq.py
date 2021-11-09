## -*- coding: utf8 -*-
import time
from time import sleep
from bs4 import BeautifulSoup
from lxml import etree
import requests
from datetime import datetime
import pyautogui as pag
import pyperclip as pc

price_std = [0] * 9
price_buf1 = [0] * 9
price_buf2 = [0] * 9
price_buf3 = [0] * 9
buf_info = [0]*9
mes = [0] * 9

##################
#####Constant#####
OPEN_TIME = (9,30)
CLOSE_TIME = (16,0)
K_MY_XY_CH = (756,346)
K_MY_XY_OK = (983,320)
K_OP_XY_CH = (747,670)
K_OP_XY_OK = (983,644)
BACK_XY = (234,8)
#####Constant#####
##################

market_open_token = [1]*9
market_close_token = [1]*9
shortsqueezelock = [1]*9
go = 0
server_token = 1
current_time = 0

pag.FAILSAFE= False
HEADERS = ({'User-Agent':
			"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36"})

class TimeOutException(Exception):
	pass
# 요청 완료
#def alarm_handler(signum,frame) :
#	print("Time is up")
#	raise TimeOutException()

class DuplicationError(Exception):
	def __init__(self):
		super().__init__("DuplicationError")

def countdown(t):
	try :
		while t:
			mins, secs = divmod(t, 60)
			timer = '{:02d}:{:02d}'.format(mins, secs)
			print(timer, end="\r")
			sleep(1)
			t -= 1
	except KeyboardInterrupt as kI:
		print(f'ERROR : {kI}')
		exit()
	except Exception as ex:
		print(f'ERROR : {ex}')


def KrwUsdconv():
	try :
		URL = "https://kr.investing.com/currencies/usd-krw"
		  
		webpage = requests.get(URL, headers=HEADERS)
		webpage.raise_for_status()
		if webpage.status_code != requests.codes.ok :
			return -1
		soup = BeautifulSoup(webpage.content, "html.parser")
		dom = etree.HTML(str(soup))
		price = float(dom.xpath('//*[@id="last_last"]')[0].text.replace(',',''))
		return price
		
	except Exception as ex:
		print(f'ERROR at currency : {ex}')


def stock_info_upd(ticker):
	try :

		URL = "https://www.investing.com/equities/" + ticker
		  
		webpage = requests.get(URL, headers=HEADERS)
		webpage.raise_for_status()
		if webpage.status_code != requests.codes.ok :
			return -1
		soup = BeautifulSoup(webpage.content, "html.parser")
		dom = etree.HTML(str(soup))
		try :
			state = dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[3]/div[1]')[0].text
		except :
			state =''
		
		if state == 'Pre Market' or state == 'After Hours' :
			price = float(dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[3]/div[2]/span')[0].text)
			try :
				variance = float(dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[3]/div[2]/div[2]/span[1]/text()[2]')[0])
			except :
				variance = float(dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[3]/div[2]/div[2]/span[1]')[0].text)
				
			try :
				variance_per = float(dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[3]/div[2]/div[2]/span[2]/text()[3]')[0])
			except :
				variance_per = float(dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[3]/div[2]/div[2]/span[2]/text()[2]')[0])
		
		else :
			price = float(dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[1]/span')[0].text)
			
			try :
				variance = float(dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[1]/div[2]/span[1]/text()[2]')[0])
			except :
				variance = float(dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[1]/div[2]/span[1]')[0].text)
			
			try :
				variance_per = float(dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[1]/div[2]/span[2]/text()[3]')[0])
			except :
				variance_per = float(dom.xpath('//*[@id="__next"]/div/div/div[2]/main/div/div[1]/div[2]/div[1]/div[2]/span[2]/text()[2]')[0])
		
		return price, variance, variance_per, '%+.2f, (%+.2f%%)' % (variance,variance_per), 1 if state == 'Pre Market' else 2 if state == 'After Hours' else 0
		
	except KeyboardInterrupt as kI:
		print(f'ERROR : {kI}')
		exit()
	#except TimeOutException as eT:
#		print(f'ERROR : {eT}')
#		stock_info_upd(ticker)
	except Exception as ex:
		print(f'ERROR crol : {ex}')
		print(current_time)
		countdown(1)
		




def judgeval(tickerfull, ticker, key, variance, inc_emoji, dec_emoji, tothemoon_emoji):
	try :
		global price_std
		global mes
		global market_open_token
		global market_close_token
		global price_buf1
		global price_buf2
		global price_buf3
		global buf_info
		global shortsqueezelock
		if current_time.hour >= 4 and current_time.hour < 21 and current_time.weekday() != 5 and current_time.weekday() != 6:
			price_info = stock_info_upd(tickerfull)
			##open notice
			if current_time.hour == OPEN_TIME[0] and current_time.minute >= OPEN_TIME[1] and price_info[4] == 0 and market_open_token[key] == 1 :
				mes[key] = f'[장 시작]\n{ticker} 주가!\n<{str(price_info[0])}$, {price_info[3]}>'
				price_std[key] = price_info[2]
				market_open_token[key] = 0
				sendPricetoKAKAO(key)
				countdown(3)
				return 0
			##close notice
			if current_time.hour == CLOSE_TIME[0] and current_time.minute >= CLOSE_TIME[1] and price_info[4] == 2 and market_close_token[key] == 1  :
				mes[key] = f'[장 종료]\n{ticker} 주가!\n<{str(buf_info[key][0])}$, {buf_info[key][3]}>'
				price_std[key] = price_info[2]
				market_close_token[key] = 0
				sendPricetoKAKAO(key)
				countdown(3)
				return 0


			#duplicationError judg
			if price_buf1[key] != price_info[0] and price_buf2[key] != price_info[0] and price_buf3 != price_info[0] :
				try :
					price_buf3[key] = price_buf2[key]
					price_buf2[key] = price_buf1[key]
					price_buf1[key] = price_info[0]
				except Exception as ex :
					print(f'{ex} 발생')
			else :
				raise DuplicationError


			print(ticker + "'s info : " + str(price_info) + " / Std% : "+ str(price_std[key]))


			

			#############

			if  price_info[2] >= 20 and price_info[2] >= (price_std[key] + variance):
				mes[key] = f'[(tothemoon_emoji)*7]\n{ticker} {"프리장 " if price_info[4] == 1 else "애프터장 " if price_info[4] == 2 else ""}주가변동!\n<{str(price_info[0])}$, {price_info[3]}>\n숏스퀴즈 예감!!!!!!!'
				price_std[key] = price_info[2]
				sendPricetoKAKAO(key)
				if shortsqueezelock[key] == 1 :
					sendPricetoKAKAOshortAlert(ticker,tothemoon_emoji)
					shortsqueezelock[key] = 0
			elif price_info[2] >= (price_std[key] + variance):
				mes[key] = f'[(inc_emoji)*4]\n{ticker} {"프리장 " if price_info[4] == 1 else "애프터장 " if price_info[4] == 2 else ""}주가변동!\n<{str(price_info[0])}$, {price_info[3]}>'
				price_std[key] = price_info[2]
				sendPricetoKAKAO(key)
			elif price_info[2] <= price_std[key] - variance:
				mes[key] = f'[(dec_emoji)*4]\n{ticker} {"프리장 " if price_info[4] == 1 else "애프터장 " if price_info[4] == 2 else ""}주가변동!\n<{str(price_info[0])}$, {price_info[3]}>'
				price_std[key] = price_info[2]
				sendPricetoKAKAO(key)

			#############
		else :
			if (current_time.hour == 23) :
				market_open_token = [1]*9
				market_close_token = [1]*9
				shortsqueezelock = [1]*9
				price_std = [0]*9
			print("준비중! 안전벨트 꽉매")
			countdown(3)
			return 0
		buf_info[key] = price_info
		countdown(3)
	except KeyboardInterrupt as kI:
		print(f'ERROR : {kI}')
		exit()
	except DuplicationError as Dp:
		print("Skip Process : {}, {}".format(ticker,price_info[0]))
		countdown(3)
	except Exception as ex:
		print(f'ERROR at judge : {ex}')
		countdown(5)

def sendPricetoKAKAO(key):
	try :
		pag.click(K_OP_XY_CH)
		sleep(0.2)
		pc.copy(mes[key])
		sleep(0.2)
		pag.keyDown('ctrl')
		pag.press('v')
		pag.keyUp('ctrl')
		print(mes[key] + " OK")
		sleep(0.2)
		pag.click(K_OP_XY_OK)
		sleep(0.2)
		pag.click(K_OP_XY_OK)
		sleep(0.2)
		pag.click(K_OP_XY_OK)
		sleep(0.2)
		pag.click(BACK_XY)
	except Exception as ex:
		print(f'ERROR : {ex}')\

def sendmestoKAKAO(mes):
	try :
		pag.click(K_OP_XY_CH)
		sleep(0.2)
		pc.copy(mes)
		sleep(0.2)
		pag.keyDown('ctrl')
		pag.press('v')
		pag.keyUp('ctrl')
		print(mes + " OK")
		sleep(0.2)
		pag.click(K_OP_XY_OK)
		sleep(0.2)
		pag.click(K_OP_XY_OK)
		sleep(0.2)
		pag.click(K_OP_XY_OK)
		sleep(0.2)
		pag.click(BACK_XY)
	except Exception as ex:
		print(f'ERROR : {ex}')

def sendPricetoKAKAOshortAlert(ticker,tothemoon_emoji):
	try :
		mes = f'[(tothemoon_emoji)*7]\n{ticker}주가 20% 상승!!!!!!\n유심히 관찰하세요'
		for i in range(5) :
			pag.click(K_OP_XY_CH)
			sleep(0.2)
			pc.copy(mes)
			sleep(0.2)
			pag.keyDown('ctrl')
			pag.press('v')
			pag.keyUp('ctrl')
			print(mes + " OK")
			sleep(0.2)
			pag.click(K_OP_XY_OK)
			sleep(0.2)
			pag.click(K_OP_XY_OK)
			sleep(0.2)
			pag.click(K_OP_XY_OK)
			sleep(0.2)
			pag.click(BACK_XY)
	except Exception as ex:
		print(f'ERROR : {ex}')

def sendPricetoKAKAOerror(er):
	try :
		pag.click(K_MY_XY_CH)
		sleep(0.2)
		pc.copy(er)
		pag.keyDown('ctrl')
		pag.press('v')
		pag.keyUp('ctrl')
		sleep(0.2)
		print(er + " OK")
		pag.click(K_MY_XY_OK)
		sleep(0.2)
		pag.click(K_MY_XY_OK)
		sleep(0.2)
		pag.click(K_MY_XY_OK)
		sleep(0.2)
		pag.click(BACK_XY)
	except Exception as ex:
		print(f'ERROR : {ex}')

def sendPricetoKAKAOServerState():
	try :
		global server_token
		if (current_time.minute%30) == 0 and server_token == 1 :
			amc = stock_info_upd("amc-entertat-hld")
			gme = stock_info_upd("gamestop-corp")
			pag.click(K_MY_XY_CH)
			sleep(0.2)
			currency = float(KrwUsdconv())
			won = currency * (amc[0]*90 + gme[0]*8)
			pc.copy(f'{str(current_time)}\n amc:{amc[0]}$ gme:{gme[0]}$\ntotal : {round(won,2)}원\n 환율{round(currency,2)}')
			pag.keyDown('ctrl')
			pag.press('v')
			pag.keyUp('ctrl')
			print(str(current_time) + " OK")
			sleep(0.2)
			pag.click(K_MY_XY_OK)
			sleep(0.2)
			pag.click(K_MY_XY_OK)
			sleep(0.2)
			pag.click(K_MY_XY_OK)
			sleep(0.2)
			pag.click(BACK_XY)
			server_token = 0
			countdown(3)
		elif (current_time.minute%30) == 5 :
			server_token = 1
	except Exception as ex:
		print(f'ERROR : {ex}')



if __name__ == "__main__":
        
	current_time = datetime.now()
	rebootserv = "서버 재가동\n" + str(current_time)
	sendmestoKAKAO(rebootserv)
	while 1:
		try:
			current_time = datetime.now()
			print(current_time)
			judgeval("amc-entertat-hld","AMC",0, 1.5,"💙","🔻","💎")
			judgeval("gamestop-corp","GME",1, 1.5,"😍","😰","🚀")
			if current_time.hour >= 4 and current_time.hour < 21 and current_time.weekday() != 5 and current_time.weekday() != 6:
				sendPricetoKAKAOServerState()
		except KeyboardInterrupt as kI:
			print(f'ERROR : {kI}')
			break
		except Exception as ex:
			print(f'ERROR : {ex}')
			countdown(5)

