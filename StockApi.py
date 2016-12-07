#!/usr/bin/env python
# -*- coding:utf8 -*-
#create at 2016.10
#author:舟尤
#email:1532121004@qq.com
#
import zmq,time
import json
import sys
from mdcliapi import MajorDomoClient
import threading
TickList ={}

class TDXApi(object):
    def __init__(self, accountID='',mdHost = "tcp://192.168.1.1:5558",boardHost= "tcp://192.168.1.1:5560",clientHost='tcp://192.168.1.1:5560'):
        global TickList
        self.accountID = accountID
        self.Position = {}   # 持仓
        self.TradedOrder = {} # 成交
        self.OrderBook = {}  # 委托
        self.Money = {}  # 资金
        self.client = MajorDomoClient(clientHost)

        context = zmq.Context()
        self.mdAPI = context.socket(zmq.SUB)
        self.mdAPI.connect(mdHost)
        self.mdAPI.setsockopt(zmq.SUBSCRIBE, b'')
        self.mdMQ = threading.Thread(target = self.recvMD )
        self.mdMQ.start()

        context = zmq.Context()
        self.boardAPI = context.socket(zmq.SUB)
        self.boardAPI.connect(boardHost)
        self.boardAPI.setsockopt(zmq.SUBSCRIBE, self.accountID)
        self.boardMQ = threading.Thread(target = self.recvBoard )
        self.boardMQ.start()
        self.init()

    def init(self):
        pass


    def recvMD(self):
        while True:
            order = self.mdAPI.recv()
            self.RtnTick(order)
    
    def recvBoard(self):
        while True:
            string = self.boardAPI.recv()
            st = string[string.index(' '):]
            js = json.loads( st )
            data = eval(st)
            if data['querytype']=='QueryOrder':
                self.OrderBook = self.RtnOrder(data)
            if data['querytype']=='QueryPosition':
                self.Position = self.RtnPosition(data)
            if data['querytype']=='QueryTraded':
                self.TradedOrder = self.RtnTraded(data)
            if data['querytype']=='QueryMoney':
                self.Money = data

    def RtnTick(self,t):
        print t

    def TradeCommit(self,InstrumentID,Direction,Volume,Price):
        o = {}
        o['Type'] = 'TradeCommit'
        o['InstrumentID'] =InstrumentID
        o['Direction'] = Direction
        o['Volume'] =Volume
        o['Price'] = Price
        ref = self.client.send(self.accountID, json.dumps(o))
        return ref

    def QueryData(self,querytype='QueryOrder'): #发出查询指令
        #querytype = {0 : 'QueryMoney', 1 : 'QueryPosition' , 2:'QueryOrder',3:'QueryTraded',4:'QueryCanCancel',5:'QueryCLID'}
        order = {'Type':querytype}
        message = self.SendRequest(order)
        return message

    def RtnOrder(self,o):  #解析委托查询
        print o 

    def RtnTraded(self,o): #解析成交查询
        return o

    def RtnPosition(self,o): #解析持仓查询
        print o

if __name__ == '__main__':
    YourID='1111111' #你的客户号
    demo = TDXApi(accountID=YourID,,mdHost = "tcp://192.168.1.1:5558",boardHost= "tcp://192.168.1.1:5560",clientHost='tcp://192.168.1.1:5560')
    #需要开通服务，可以联系 qq:1532121004
    while True:
        #print len(TickList.keys())
        demo.TradeCommit('510300','B',100,3.305)
        time.sleep(10)
