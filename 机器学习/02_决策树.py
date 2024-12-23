# -*- coding: UTF-8 -*-
from matplotlib.font_manager import FontProperties
import matplotlib.pyplot as plt
from math import log
import operator

def createDataSet():
    # 创建一个数据集和标签列表
    dataSet = [
        [0, 0, 0, 0, 'no'],
        [0, 0, 0, 1, 'no'],
        [0, 1, 0, 1, 'yes'],
        [0, 1, 1, 0, 'yes'],
        [0, 0, 0, 0, 'no'],
        [1, 0, 0, 0, 'no'],
        [1, 0, 0, 1, 'no'],
        [1, 1, 1, 1, 'yes'],
        [1, 0, 1, 2, 'yes'],
        [1, 0, 1, 2, 'yes'],
        [2, 0, 1, 2, 'yes'],
        [2, 0, 1, 1, 'yes'],
        [2, 1, 0, 1, 'yes'],
        [2, 1, 0, 2, 'yes'],
        [2, 0, 0, 0, 'no']
    ]
    labels = ['F1-AGE', 'F2-WORK', 'F3-HOME', 'F4-LOAN']  # 特征标签
    return dataSet, labels

def createTree(dataset, labels, featLabels):
    # 递归构造决策树
    classList = [example[-1] for example in dataset]  # 获取所有类标签
    if classList.count(classList[0]) == len(classList):  # 如果数据集中只有一个类标签，则直接返回该标签
        return classList[0]
    if len(dataset[0]) == 1:  # 如果数据集中的特征已经用完，则返回出现次数最多的类标签
        return majorityCnt(classList)
    bestFeature = chooseBestFeatureToSplit(dataset)  # 选择最好的数据集划分方式
    bestFeatureLabel = labels[bestFeature]  # 获取最好的特征标签
    featLabels.append(bestFeatureLabel)  # 将最好的特征标签加入到featLabels中
    myTree = {bestFeatureLabel: {}}  # 根据最好的特征标签创建树
    del labels[bestFeature]  # 删除已使用的特征标签
    featValues = [example[bestFeature] for example in dataset]  # 获取最好的特征包含的所有属性值
    uniqueVals = set(featValues)  # 去掉重复的属性值
    for value in uniqueVals:  # 遍历当前选择特征包含的所有属性值
        sublabels = labels[:]  # 复制所有特征标签，保证每次递归调用时不改变原始列表
        myTree[bestFeatureLabel][value] = createTree(
            splitDataSet(dataset, bestFeature, value),
            sublabels,
            featLabels
        )  # 递归构造子树
    return myTree

def majorityCnt(classList):
    # 返回出现次数最多的类标签
    classCount = {}
    for vote in classList:
        if vote not in classCount.keys():
            classCount[vote] = 0
        classCount[vote] += 1
    sortedClassCount = sorted(classCount.items(), key=operator.itemgetter(1), reverse=True)
    return sortedClassCount[0][0]

def chooseBestFeatureToSplit(dataset):
    # 选择最好的数据集划分方式
    numFeatures = len(dataset[0]) - 1  # 特征数量
    baseEntropy = calcShannonEnt(dataset)  # 计算整个数据集的信息熵
    bestInfoGain = 0
    bestFeature = -1
    for i in range(numFeatures):  # 遍历所有特征
        featList = [example[i] for example in dataset]
        uniqueVals = set(featList)  # 获取该特征下的所有唯一属性值
        newEntropy = 0
        for val in uniqueVals:  # 计算该特征下每个属性值的信息熵
            subDataSet = splitDataSet(dataset, i, val)
            prob = len(subDataSet) / float(len(dataset))
            newEntropy += prob * calcShannonEnt(subDataSet)
        infoGain = baseEntropy - newEntropy  # 计算信息增益
        if infoGain > bestInfoGain:  # 选择信息增益最大的特征
            bestInfoGain = infoGain
            bestFeature = i
    return bestFeature

def splitDataSet(dataset, axis, val):
    # 按照给定特征划分数据集
    retDataSet = []
    for featVec in dataset:
        if featVec[axis] == val:
            reducedFeatVec = featVec[:axis]
            reducedFeatVec.extend(featVec[axis + 1:])
            retDataSet.append(reducedFeatVec)
    return retDataSet

def calcShannonEnt(dataset):
    # 计算给定数据集的信息熵
    numExamples = len(dataset)
    labelCounts = {}
    for featVec in dataset:
        currentLabel = featVec[-1]
        if currentLabel not in labelCounts.keys():
            labelCounts[currentLabel] = 0
        labelCounts[currentLabel] += 1
    shannonEnt = 0
    for key in labelCounts:
        prop = float(labelCounts[key] / numExamples)
        shannonEnt -= prop * log(prop, 2)
    return shannonEnt

def getNumLeafs(myTree):
    # 获取决策树的叶子节点数目
    numLeafs = 0
    firstStr = next(iter(myTree))
    secondDict = myTree[firstStr]
    for key in secondDict.keys():
        if isinstance(secondDict[key], dict):
            numLeafs += getNumLeafs(secondDict[key])
        else:
            numLeafs += 1
    return numLeafs

def getTreeDepth(myTree):
    # 获取决策树的深度
    maxDepth = 0
    firstStr = next(iter(myTree))
    secondDict = myTree[firstStr]
    for key in secondDict.keys():
        if isinstance(secondDict[key], dict):
            thisDepth = 1 + getTreeDepth(secondDict[key])
        else:
            thisDepth = 1
        if thisDepth > maxDepth:
            maxDepth = thisDepth
    return maxDepth

def plotNode(nodeTxt, centerPt, parentPt, nodeType):
    # 绘制带箭头的注解
    arrow_args = dict(arrowstyle="<-")
    font = FontProperties(fname=r"c:\windows\fonts\simsunb.ttf", size=14)  # 设置字体

    createPlot.ax1.annotate(nodeTxt, xy=parentPt, xycoords='axes fraction',
                            xytext=centerPt, textcoords='axes fraction',
                            va="center", ha="center", bbox=nodeType, arrowprops=arrow_args,
                            fontproperties=font)

def plotMidText(cntrPt, parentPt, txtString):
    # 在父子节点间填充文本信息
    xMid = (parentPt[0] - cntrPt[0]) / 2.0 + cntrPt[0]
    yMid = (parentPt[1] - cntrPt[1]) / 2.0 + cntrPt[1]
    createPlot.ax1.text(xMid, yMid, txtString, va="center", ha="center", rotation=30)

def plotTree(myTree, parentPt, nodeTxt):
    # 绘制决策树
    decisionNode = dict(boxstyle="sawtooth", fc="0.8")  # 设置决策节点样式
    leafNode = dict(boxstyle="round4", fc="0.8")  # 设置叶子节点样式
    numLeafs = getNumLeafs(myTree)
    depth = getTreeDepth(myTree)
    firstStr = next(iter(myTree))
    cntrPt = (plotTree.xOff + (1.0 + float(numLeafs)) / 2.0 / plotTree.totalW, plotTree.yOff)
    plotMidText(cntrPt, parentPt, nodeTxt)
    plotNode(firstStr, cntrPt, parentPt, decisionNode)
    secondDict = myTree[firstStr]
    plotTree.yOff = plotTree.yOff - 1.0 / plotTree.totalD
    for key in secondDict.keys():
        if isinstance(secondDict[key], dict):
            plotTree(secondDict[key], cntrPt, str(key))
        else:
            plotTree.xOff = plotTree.xOff + 1.0 / plotTree.totalW
            plotNode(secondDict[key], (plotTree.xOff, plotTree.yOff), cntrPt, leafNode)
            plotMidText((plotTree.xOff, plotTree.yOff), cntrPt, str(key))
    plotTree.yOff = plotTree.yOff + 1.0 / plotTree.totalD

def createPlot(inTree):
    # 创建图形并清除
    fig = plt.figure(1, facecolor='white')
    fig.clf()
    axprops = dict(xticks=[], yticks=[])
    createPlot.ax1 = plt.subplot(111, frameon=False, **axprops)
    plotTree.totalW = float(getNumLeafs(inTree))
    plotTree.totalD = float(getTreeDepth(inTree))
    plotTree.xOff = -0.5 / plotTree.totalW;
    plotTree.yOff = 1.0
    plotTree(inTree, (0.5, 1.0), '')
    plt.show()

if __name__ == '__main__':
    dataSet, labels = createDataSet()  # 创建数据集
    featLabels = []  # 用于存储选择的特征标签
    myTree = createTree(dataSet, labels, featLabels)  # 构建决策树
    print(featLabels)  # 输出选择的特征标签
    createPlot(myTree)  # 绘制决策树