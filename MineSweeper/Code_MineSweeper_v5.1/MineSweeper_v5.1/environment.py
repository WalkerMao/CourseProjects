import pygame
import sys
import random
from agent import agent
from baseline import baseline
import numpy as np
import matplotlib.pyplot as plt


class sweep(object):

    def __init__(self, dim, n, winFlag=True, uncertainModel='none', knowN=True):
        self.winFlag = winFlag
        self.dim = dim # dimension
        self.n = n # mine number
        if self.winFlag:
            self.winSize = ((800//dim)*dim, (600//dim)*dim) # window size
            self.win = pygame.display.set_mode(self.winSize) # initialize the window
            self.unitW = self.winSize[0]//self.dim # width of one grid
            self.unitH = self.winSize[1]//self.dim # height of one grid
            self.drawBox() # draw board (box)
            self.loadImg()  # load images
        # initialize the board (box)
        self.box = [[0 for _ in range(self.dim)] for _ in range(self.dim)]
        # boxView is a matrix, where 0~8 are number of mines in surrounding, 
        # 9 is flag, 10 is unvisited, 11 is uncovered but not information
        self.boxView = [[10 for _ in range(self.dim)] for _ in range(self.dim)]
        self.mine = set() # positions of mines
        self.visited = set() # visited positions
        self.put_mine() # put mines in board 
        self.visitedFlag = set()
        self.bombed = set()
        self.number = dict()
        self.isTrueClick = False
        self.success = False
        self.score = 0
        self.uncertainModel = uncertainModel
        self.knowN = knowN

      # print(pygame.display.Info())


    # draw lines
    def drawBox(self):
        if self.winFlag:
            self.win.fill((169, 169, 169))  # grey
            # draw horizontal line
            for i in range(self.dim-1):
                pygame.draw.line(self.win, (255, 255, 255), (0,
                                self.unitH * (i+1)), (self.winSize[0], self.unitH * (i+1)))
            # draw vertical line
            for i in range(self.dim-1):
                pygame.draw.line(self.win, (255, 255, 255), (self.unitW *
                                (i+1), 0), (self.unitW * (i+1), self.winSize[1]))
    

    # load images
    def loadImg(self):
        if self.winFlag:
            self.unitOpen = pygame.image.load('image/box.png').convert_alpha()
            self.unitClose = pygame.image.load('image/box_sweep.png').convert_alpha()
            self.mine1 = pygame.image.load('image/mine1.png').convert_alpha()
            self.mine2 = pygame.image.load('image/mine2.jpg').convert_alpha()
            self.num1 = pygame.image.load('image/num1.png').convert_alpha()
            self.num2 = pygame.image.load('image/num2.png').convert_alpha()
            self.num3 = pygame.image.load('image/num3.png').convert_alpha()
            self.num4 = pygame.image.load('image/num4.png').convert_alpha()
            self.num5 = pygame.image.load('image/num5.png').convert_alpha()
            self.num6 = pygame.image.load('image/num6.png').convert_alpha()
            self.num7 = pygame.image.load('image/num7.png').convert_alpha()
            self.num8 = pygame.image.load('image/num8.png').convert_alpha()
            self.flag = pygame.image.load('image/flag.png').convert_alpha()

            self.unitOpen = pygame.transform.scale(self.unitOpen, (self.unitW, self.unitH))
            self.unitClose = pygame.transform.scale(self.unitClose, (self.unitW, self.unitH))
            self.mine1 = pygame.transform.scale(self.mine1, (self.unitW, self.unitH))
            self.mine2 = pygame.transform.scale(self.mine2, (self.unitW, self.unitH))
            self.num1 = pygame.transform.scale(self.num1, (self.unitW, self.unitH))
            self.num2 = pygame.transform.scale(self.num2, (self.unitW, self.unitH))
            self.num3 = pygame.transform.scale(self.num3, (self.unitW, self.unitH))
            self.num4 = pygame.transform.scale(self.num4, (self.unitW, self.unitH))
            self.num5 = pygame.transform.scale(self.num5, (self.unitW, self.unitH))
            self.num6 = pygame.transform.scale(self.num6, (self.unitW, self.unitH))
            self.num7 = pygame.transform.scale(self.num7, (self.unitW, self.unitH))
            self.num8 = pygame.transform.scale(self.num8, (self.unitW, self.unitH))
            self.flag = pygame.transform.scale(self.flag, (self.unitW, self.unitH))


    def put_mine(self):
        i = 0
        # put n mines randomly
        while i < self.n:  
            x = random.randint(0, self.dim-1)
            y = random.randint(0, self.dim-1)
            if self.box[x][y] == 0:
                self.box[x][y] = 1  # set mine = 1
                self.mine.add((x,y))
                i = i + 1
               
    # show the number of surrounding mines
    def numMine(self,pos) -> int:
        n = 0
        y, x = pos[1], pos[0]
        move = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        for m in move:
            if 0<=x+m[0]<self.dim and 0<=y+m[1]<self.dim and self.box[x+m[0]][y+m[1]]==1:
                n += 1
        self.number[pos] = n
        return n


    # traverse surrounding until find mine or flag or visited
    def recursion(self, pos):
        # if pos is not flag or number or visited
        if not (pos in self.visited or pos in self.visitedFlag): 
            n = self.numMine(pos)
            if self.box[pos[0]][pos[1]] == 0:
                if n > 0: # there are mine(s) in surrounding
                    self.setNum(pos, n) # set number
                    self.boxView[pos[0]][pos[1]] = n
                    self.uncertain(pos[0], pos[1], p=0.5)
                    self.visited.add(pos) 
                # No mine in surround
                elif self.box[pos[0]][pos[1]] == 0:
                    self.setNull(pos)
                    self.visited.add(pos)
                    self.boxView[pos[0]][pos[1]] = 0
                    x, y = pos[0], pos[1]
                    move = [(-1,0), (0,-1), (0,1), (1,0)]
                    
                    for m in move:
                        if 0<=x+m[0]<self.dim and 0<=y+m[1]<self.dim:
                            self.recursion((x+m[0], y+m[1]))
        
   
    # cancel flags
    def recover(self, pos) -> None:
        if self.winFlag:
            pygame.draw.rect(self.win, (169,169,169),(pos[1]*self.unitW,pos[0]*self.unitH,self.unitW,self.unitH))


    # No mines in surround
    def setNull(self,pos) -> None:
        if self.winFlag:
            self.win.blit(self.unitClose,(self.unitW*pos[1],self.unitH*pos[0]))
    
    
    def setFlag(self, pos) -> None:
        if self.winFlag:
            self.win.blit(self.flag,(self.unitW*pos[1],self.unitH*pos[0]))        
    
    
    # if success, show all mines
    def setMine(self) -> None:
        if self.winFlag:
            self.success = True
            for posMine in self.mine:
                self.win.blit(self.mine1,(self.unitW*posMine[1],self.unitH*posMine[0]))
            s = "Finished! Detected mines: {}. Total mines: {}.".format(len(self.mine)-len(self.bombed), len(self.mine))
            print(s)
            self.score = (len(self.mine)-len(self.bombed))/len(self.mine)
            # Tk().wm_withdraw() # to hide the main window
            # messagebox.showinfo('Finished!', s)
            myfont = pygame.font.SysFont('Comic Sans MS', 35)
            textsurface = myfont.render(s, False, (0, 0, 0))
            self.win.blit(textsurface,(0,0))
        
    
    # mine bomb
    def bomb(self,pos) -> None:
        self.win.blit(self.mine2,(self.unitW*pos[1],self.unitH*pos[0]))
        print("Boom!")
    

    # show number
    def setNum(self, pos, n=None):
        if self.winFlag:
            if n == None:
                n = self.numMine(pos)
            pygame.draw.rect(self.win, (230,230,230), (pos[1]*self.unitW,pos[0]*self.unitH,self.unitW,self.unitH))
            pngList = [self.unitClose, self.num1, self.num2, self.num3, self.num4, self.num5, self.num6, self.num7, self.num8]
            self.win.blit(pngList[n],(self.unitW*pos[1],self.unitH*pos[0]))


    def autoReact(self, mouseLeft, mouseRight, pos):
        if mouseLeft == 1 and pos not in self.visited and pos not in self.visitedFlag:                
            if self.box[pos[0]][pos[1]] == 1: # meet a mine
                self.visitedFlag.add(pos)
                self.bombed.add(pos)
                self.boxView[pos[0]][pos[1]] = 9 # 9 means flag
          
            else:
                self.recursion(pos)

            if self.mine == self.visitedFlag: 
                self.success = True # success
                self.score = (len(self.mine)-len(self.bombed))/len(self.mine)
                
        # right button to set or cancel the flag
        elif mouseRight == 1 and pos not in self.visited and pos not in self.bombed: 
            # cancel the flag
            if pos in self.visitedFlag:
                self.visitedFlag.remove(pos)
                self.boxView[pos[0]][pos[1]] = 10 # 10 means covered (unvisited)
              
            # set the flag
            else:
            #    self.setFlag(pos)
                self.visitedFlag.add(pos)
                self.boxView[pos[0]][pos[1]] = 9 # 9 means flag

            if len(self.visited) + len(self.visitedFlag) == self.dim**2 and \
                self.mine == self.visitedFlag: 

                self.success = True # success
                self.score = (len(self.mine)-len(self.bombed))/len(self.mine)
        
        # True left button to check whether it is successful
        elif self.isTrueClick and self.mine == self.visitedFlag:
            self.success = True # success
            self.score = (len(self.mine)-len(self.bombed))/len(self.mine) 
              
    

    def react(self, mouseLeft, mouseRight, pos):
        # left button to meet the mine or start recursion
        if mouseLeft == 1 and pos not in self.visited and pos not in self.visitedFlag:                
            if self.box[pos[0]][pos[1]] == 1: # meet a mine
                self.visitedFlag.add(pos)
                self.bombed.add(pos)
                self.boxView[pos[0]][pos[1]] = 9 # 9 means flag
                self.bomb(pos)
            else:
                self.recursion(pos)

            if self.mine == self.visitedFlag: 
                self.setMine() # success
                
        # right button to set or cancel the flag
        elif mouseRight == 1 and pos not in self.visited and pos not in self.bombed: 
            # cancel the flag
            if pos in self.visitedFlag:
                self.visitedFlag.remove(pos)
                self.boxView[pos[0]][pos[1]] = 10 # 10 means covered (unvisited)
                self.recover(pos) 
            # set the flag
            else:
                self.setFlag(pos)
                self.visitedFlag.add(pos)
                self.boxView[pos[0]][pos[1]] = 9 # 9 means flag

            if len(self.visited) + len(self.visitedFlag) == self.dim**2 and \
                self.mine == self.visitedFlag: 

                self.setMine() # success
        
        # True left button to check whether it is successful
        elif self.isTrueClick and self.mine == self.visitedFlag: 
            self.setMine() # success
            
    def getScore(self):
        return self.score


    def uncertain(self, i:int, j:int, p:float=0.3) -> None:
        if self.uncertainModel == "none":
            None
        elif self.uncertainModel == "lostInformation" and random.random() < p:
            self.boxView[i][j] = 11
        elif self.uncertainModel == "underestimate":
            self.boxView[i][j] = random.randint(0, self.boxView[i][j])
        elif self.uncertainModel == "overestimate":
            self.boxView[i][j] = random.randint(self.boxView[i][j], 8)
        # else:
        #     raise ValueError("No uncertianModel named {}! Please input 'none', 'lostInformation',\
        #                      'underestimate' or 'overestimate'".format(uncertainModel))


    def show(self, isRobot=True, needClick=True, splitBorders=True): 
      #  if isRobut and (not needClick):
        if not self.winFlag:
            while not self.success:
                myAgent = agent(n=self.n, boxView=self.boxView, knowN=self.knowN, \
                                splitBorders=splitBorders, uncertainModel=self.uncertainModel)
                for mouseLeft, mouseRight, pos in myAgent.tank():
                    self.autoReact(mouseLeft, mouseRight, pos)
        else:
            self.drawBox()
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        sys.exit()
                    elif event.type == pygame.MOUSEBUTTONDOWN:
                        mouseLeft, mouseMid, mouseRight = pygame.mouse.get_pressed()   
                        if isRobot:
                            if mouseLeft:
                                self.isTrueClick = True
                                # mouseLeft, mouseRight, pos = 1,0,(0,0)
                                myAgent = agent(n=self.n, boxView=self.boxView, knowN=self.knowN, \
                                                splitBorders=splitBorders, uncertainModel=self.uncertainModel)
                                for mouseLeft, mouseRight, pos in myAgent.tank():
                                    self.react(mouseLeft, mouseRight, pos)
                                    # deal with uncertaintity
                                    if mouseLeft and 0<=self.boxView[pos[0]][pos[1]]<=8:
                                        self.uncertain(i=pos[0], j=pos[1], p=0.5) 
                        else:
                            mousePos = pygame.mouse.get_pos()
                            pos = (mousePos[1]//self.unitH, mousePos[0]//self.unitW)
                            self.react(mouseLeft, mouseRight, pos)
                        # print(self.boxView)
                    
                    pygame.display.update()

    def baseShow(self,needClick=True):
       
        self.drawBox()
        if not needClick:
            while not self.success:
                myBase = baseline(n=self.n, boxView=self.boxView)
                for mouseLeft, mouseRight, pos in myBase.base():
                    self.autoReact(mouseLeft, mouseRight, pos)

        while needClick:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:      
                    myBase = baseline(n=self.n, boxView=self.boxView)
                    for mouseLeft, mouseRight, pos in myBase.base():
                        self.react(mouseLeft, mouseRight, pos)
                pygame.display.update()
        

if __name__ == '__main__':
    pygame.init()
    dimension = 10
    mineNum = 20
    baseScoreList = list()
    scoreList = list()
    density = list()
    times = 10
    resultChoose = 1
    #compare the basic and improved algorithm
    if resultChoose == 1:
        for mineNum in range(5,80,5):
            score = 0
            for i in range(times):
               # app = sweep(dimension, mineNum, winFlag=False, uncertainModel='none', knowN=True)
              #  app.show(isRobot=True, needClick=False, splitBorders=True)
                app = sweep(dimension,mineNum,False)
                app.baseShow(False)      
                score = app.getScore() + score
            baseScoreList.append(score/times)
            density.append(mineNum/(dimension*dimension))
        for mineNum in range(5,80,5):
            score = 0
            for i in range(times):
                app = sweep(dimension, mineNum, winFlag=False, uncertainModel='none', knowN=False)
                app.show(isRobot=True, needClick=False, splitBorders=True)      
                score = app.getScore() + score
            scoreList.append(score/times)
        baseScoreList = np.array(baseScoreList)
        scoreList = np.array(scoreList)
        density = np.array(density)    
        plt.plot(density,scoreList,color = "blue",label = "improved")
        plt.plot(density,baseScoreList,color = "orange",label = "baseline")   
        plt.ylabel('score')
        plt.xlabel('density')
        plt.title('score VS density with dim 10')
        plt.legend()
        plt.show()
    #when the agent know the mine number
    if resultChoose == 2:
        for mineNum in range(5,80,5):
            score = 0
            for i in range(times):
                app = sweep(dimension, mineNum, winFlag=False, uncertainModel='none', knowN=True)
                app.show(isRobot=True, needClick=False, splitBorders=True)      
                score = app.getScore() + score
            scoreList.append(score/times)
            density.append(mineNum/(dimension*dimension))
        scoreList = np.array(scoreList)
        density = np.array(density)
        plt.plot(density,scoreList,color = "blue")
        plt.ylabel('score')
        plt.xlabel('density')
        plt.title('score VS density with dim 10')     
        plt.show()
    #basic algorithm show
    if resultChoose == 3:
        app = sweep(dimension,mineNum,True)
        app.baseShow(True)  
    #improved algorithm show
    if resultChoose == 4:
        app = sweep(dimension, mineNum, winFlag=True, uncertainModel='none', knowN=True)
        app.show(isRobot=True, needClick=True, splitBorders=True) 
    #manual mine sweeper    
    if resultChoose == 5:
        app = sweep(dimension, mineNum, winFlag=True, uncertainModel='none', knowN=True)
        app.show(isRobot=False,needClick=True)
    #uncertainty
    if resultChoose == 6:
        dimension = 5
        times = 60
        for mineNum in range(2,26,2):
            score = 0
            for i in range(times):
                if i%10==0: print('i', i, 'MineNum:', mineNum)
                app = sweep(dimension, mineNum, winFlag=False, uncertainModel='underestimate', knowN=True)
                app.show(isRobot=True, needClick=False, splitBorders=True)      
                score = app.getScore() + score
            scoreList.append(score/times)
            density.append(mineNum/(dimension*dimension))
        scoreList = np.array(scoreList)
        # print(scoreList)
        density = np.array(density)
        plt.plot(density,scoreList,color = "blue")
        plt.ylabel('score')
        plt.xlabel('density')
        plt.title('score VS density with dim 5')     
        plt.show()
