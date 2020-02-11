from copy import deepcopy
import random

class agent(object):

    def __init__(self, n:int, boxView:list, knowN:bool, splitBorders:bool, uncertainModel:str):
        self.n = n # mine number
        self.dim = len(boxView)
        self.boxView = boxView # [[]] two dimension arrays
        self.move = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
        self.borderValues = list() # [{():}]
        # ans: [mouseLeft, mouseRight, pos] e.x. [1,0,(0,0)] click left button at position (0,0)
        self.ans = list() 
        self.inside = tuple() # an unvisited grid that is not border
        self.nUnvisited = 0 # number of unvisited grids
        self.nFlag = 0 
        self.knowN = knowN
        self.splitBorders = splitBorders
        self.uncertainModel = uncertainModel

    # the `borders` variable is the list of border
    # border is the list of connective border nodes in surrounding of num nodes. 
    # e.x. num node is (0,0), and the border will be [(0,1), (0,2), (1,0)]
    def getBorders(self) -> list:
        borders = list()
        # `borderNodesList` is a list of all borders nodes in current map (`boxView`)
        borderNodesList = list() # [(), (), (), ...]
        
        for i in range(self.dim):
            for j in range(self.dim):
                if self.boxView[i][j] == 10: # 10 means unvisited
                    self.nUnvisited += 1
                elif self.boxView[i][j] == 9: # 9 means flag
                    self.nFlag += 1
                # num nodes and lost information nodes
                elif 1 <= self.boxView[i][j] <= 8 or self.boxView[i][j]==11:
                    for m0, m1 in self.move:
                        if 0<=i+m0<self.dim and 0<=j+m1<self.dim \
                           and self.boxView[i+m0][j+m1] == 10:
                            
                            borderNodesList.append((i+m0, j+m1))

        borderNodesSet = set(borderNodesList)

        # find a unvisited node that is not border node
        # if we cannot get solution by tank algorithm, we left click this node
        for i in range(self.dim):
            if self.inside: break
            for j in range(self.dim):
                if self.boxView[i][j] == 10 \
                    and (i,j) not in borderNodesSet:

                    self.inside = (i,j)
                    break

        # a helper function to do recursion to find an adjacent node of (i,j)
        # and then append the adjacent node to one border list
        def findAdjacent(i:int, j:int, oneBorder:list):
            for m0, m1 in self.move:
                if (i+m0, j+m1) in borderNodesSet:
                    oneBorder.append((i+m0, j+m1))
                    borderNodesSet.remove((i+m0, j+m1))
                    findAdjacent(i+m0, j+m1, oneBorder)

        # use `findAdjacent`, seperate connective nodes in `borderNodesList` to `borders`
        if self.splitBorders:
            while borderNodesList:
                i,j = borderNodesList.pop()
                if (i,j) in borderNodesSet:
                    oneBorder = [(i,j)]
                    borderNodesSet.remove((i, j))
                    findAdjacent(i, j, oneBorder)
                    borders.append(oneBorder)
        else:
            borders = [borderNodesList] if borderNodesList else []
        
        # print(borders)
        return borders


    # the border node (i,j) has been set a value in borderDict
    # this function check whether this value can statisfy the num node in surrounding
    def check(self, i, j, borderSet, borderDict):
        for m0, m1 in self.move:
            if 0<=i+m0<self.dim and 0<=j+m1<self.dim and 1 <= self.boxView[i+m0][j+m1] <= 8:

                # the num node around border node
                iNum, jNum = i+m0, j+m1 
                # check whether borderDict can satisfy the num node
                tempSum = 0
                nNan = 0 # nNanBorderOfNum, number of NaN border nodes around num node (iNum,jNum)
                nFlagAround = 0
                nLostInfo = 0 # number of lost information nodes(11) around num node (iNum,jNum)
                # for every num node around the node (i,j)
                # check whether this num node can be satisfied by the values in `borderDict`
                for m0, m1 in self.move:
                    if 0<=iNum+m0<self.dim and 0<=jNum+m1<self.dim:
                        # 9 means flag
                        if self.boxView[iNum+m0][jNum+m1] == 9:
                            nFlagAround += 1
                        # node that is unvisited and not in `borderDict`
                        elif self.boxView[iNum+m0][jNum+m1] == 10 \
                            and (iNum+m0, jNum+m1) not in borderDict: 
                            nNan += 1 
                        
                        if (iNum+m0, jNum+m1) in borderDict:
                            tempSum += borderDict[(iNum+m0, jNum+m1)]
                
                # if borderDict cannot satisfy this num node (iNum, jNum), then keep searching
                if self.uncertainModel == 'none' or self.uncertainModel == "lostInformation":
                    if tempSum + nNan + nFlagAround < self.boxView[iNum][jNum] or \
                        tempSum + nFlagAround > self.boxView[iNum][jNum]:
                        return False
                ########
                elif self.uncertainModel == 'underestimate':
                    if tempSum + nNan + nFlagAround < self.boxView[iNum][jNum]:
                        return False
                elif self.uncertainModel == 'overestimate':
                    if tempSum + nFlagAround > self.boxView[iNum][jNum]:
                        return False
                else:
                    print("Error")
                ########
        return True


    # dfs to do exhaustivity
    # border(list): [(),(),...]. borderSet(set): {(),(),...}. borderDict(dict): {():,():,...}
    def dfs(self, k:int, border:list, borderSet:set, borderDict:dict):
        if border:
            i,j = border.pop()
            borderDict[(i,j)] = 0 # set value of this pos (i,j) to 0 (no mine)
            # use check function to check whether the value of (i,j) is valid
            if self.check(i, j, borderSet, borderDict):
                self.dfs(k, border.copy(), borderSet, borderDict.copy())
            # similar
            borderDict[(i,j)] = 1
            if self.check(i, j, borderSet, borderDict):
                self.dfs(k, border.copy(), borderSet, borderDict.copy())
        else:
            self.borderValues[k].append(borderDict.copy())


    # used to merge the values in different dict to a mean value, 
    # which is the probability of this pos to be 1 (mine)
    # dictList: [{(): }, {(): }, ...]
    # dictList = [borderDict0, borderDict1, ...]
    # e.x. dictList=[{(0,0):0, (0,1):1}, {(0,0):1, (0,1):1}], return {(0,0):0.5, (0,1):1.0}
    def mergeDict(self, dictList: list) -> dict:
        if dictList:
            out = dictList[0].copy()
            for pos in out:
                out[pos] = [out[pos]]
            for d in dictList[1:]:
                for pos in d:
                    if pos not in out:
                        out[pos] = list()
                    out[pos].append(d[pos])
            for pos in out:
                # estimate probability
                out[pos] = sum(out[pos]) / len(out[pos])
            return out


    def tank(self):
        # print(self.boxView)
        bordersList = self.getBorders()
        self.borderValues = [[] for _ in range(len(bordersList))]
        for k in range(len(bordersList)):
            self.dfs(k, deepcopy(bordersList[k]), set(bordersList[k]), dict())
            self.borderValues[k] = self.mergeDict(self.borderValues[k])
        
        minProb, minPos = 1.1, (0,0)
        if self.knowN and self.inside:
            if self.nUnvisited!=0: 
                minProb = (self.n - self.nFlag) / self.nUnvisited
            # initialize a position
            minPos = self.inside

        for borderValDict in self.borderValues:
            if borderValDict:
                for pos in borderValDict:
                    # pos is certain to be 0 (no mine). Left button to visit.
                    if borderValDict[pos] == 0.0:
                        self.ans.append((1, 0, pos))
                    # pos is certain to be 1 (mine). Right button to set flag.
                    elif borderValDict[pos] == 1.0:
                        self.ans.append((0, 1, pos))
                    elif borderValDict[pos] < minProb:
                        minProb = borderValDict[pos]
                        minPos = pos
        
        # if there is no position is certain to be 0 or 1,
        # then click left button on the position with lowest probability to be 1 (mine).
        if not self.ans:
            if minProb<1.1:
                self.ans.append((1, 0, minPos))
                # print("random node in border")
            else:
                if not self.inside:
                    self.inside = (0,0)
                self.ans.append((1, 0, self.inside))
                # print("random node inside (not border)")
        

        # print("ans", self.ans)
        return self.ans
        
        

if __name__ == '__main__':
    boxView = [[10, 10, 10], [1, 2, 2], [0, 0, 0]]
    agent(2, boxView).tank()
