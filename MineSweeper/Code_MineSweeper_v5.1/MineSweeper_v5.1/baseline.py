import random
class baseline(object):

    def __init__(self, n:int, boxView:list):
        self.n = n # mine number
        self.dim = len(boxView)
        self.boxView = boxView # [[]] two dimension arrays
        self.move = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
       
        
       

    def base(self):
        ans = list()#save position of cells which we plan to click
        for i in range(self.dim):
            for j in range(self.dim):
                totalMine = 0
                totalSafe = 0
                totalClose = 0
                total = 0      

                if 0 < self.boxView[i][j] < 9 : #find cells on the border
                    clue = self.boxView[i][j]
                    for m in self.move:
                        if 0 <= i+m[0]< self.dim and 0 <= j+m[1] < self.dim:
                            total = total + 1#total cell number around
                          
                            if self.boxView[i+m[0]][j+m[1]] < 9:#safe cell
                                totalSafe = totalSafe + 1
                            if self.boxView[i+m[0]][j+m[1]]  == 9:#mine cell
                                totalMine = totalMine + 1 
                            if self.boxView[i+m[0]][j+m[1]]  == 10:#hidden cell
                                totalClose = totalClose + 1 
               
                    if totalClose == 0:#no hidden cell around
                        continue
                    if (total - clue - totalSafe) == totalClose: # safe
                        for m in self.move:
                            if 0 <= i+m[0] < self.dim and 0 <= j+m[1] < self.dim and \
                                self.boxView[i+m[0]][j+m[1]]  == 10:
                                ans.append((1,0,(i+m[0],j+m[1])))
                        break
                  
                    if (clue - totalMine) == totalClose:# mine and setFlag
                        for m in self.move:
                            if 0 <= i+m[0]< self.dim and 0 <= j+m[1] < self.dim and \
                                self.boxView[i+m[0]][j+m[1]]  == 10:
                                ans.append((0,1,(i+m[0],j+m[1])))
                        break                      
            if ans: break
                    
        if not ans:#randomly pick another cell to reveal
            x = 1
            y = 1
            while self.boxView[x][y] != 10:
                x = random.randint(0, self.dim -1)  
                y = random.randint(0, self.dim -1)           
            ans.append((1,0,(x,y)))
               
        return ans    

