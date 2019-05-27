import re
import math
from os import system
import sys
import traceback


def inlst(lst, value, key=lambda x:x):
        for i in range(len(lst)):
            each = lst[i]
            if key(each) == value:
                return i
        return -1

recipes = {}

def main():

    global recipes

    prog = re.compile(r'"(.+?)"')
    progcnt = re.compile(r'@count:([0-9]+?)')



    print(r'''    IC2合成计算器 alpha v1.0.3
    作者: 墨滢
    详细使用说明见“使用说明.txt”，更新见“更新记录.txt”
    发现bug请将截图发给我，十分感谢
''')


    # 读取汉化

    with open('itempanel.csv','r',encoding='gb18030') as f:
        data = f.read().splitlines()

    del data[0]
    for i in range(len(data)):
        each = data[i].split(',')
        data[i] = each.copy()
        #print(data[0],data[1],data[2])
    data.sort(key=lambda x:int(x[2]))
    translate = {}

    for each in data:
        itemname = each[0]
        itemmeta = int(each[2])
        tranname = each[4]
        if itemname not in translate:
            translate[itemname] = tranname
        translate['%s@%s'%(itemname,itemmeta)] = tranname

    print('[INFO]读取到%s条汉化文本'%len(translate))

    # 读取OreDict

    with open('oredict.csv','r',encoding='gb18030') as f:
        data = f.read().splitlines()

    del data[0]
    oredict = {}

    for e in data:
        each = e.split(',')
        orename = 'OreDict:'+each[0]
        itemid = each[2]
        itemmeta = each[1]
        if itemmeta.count('@') != 0:
            itemmeta = itemmeta.split('@')[1]
        else:
            itemmeta = 0

        if orename not in oredict:
            oredict[orename] = '%s@%s'%(itemid,itemmeta)

    oredict['Fluid:water'] = 'minecraft:water_bucket@*'

    print('[INFO]读取到%s条矿物词典规则'%len(oredict))

    recipes = {}

    # 读取有序合成表

    with open('./config/有序.ini','r',encoding='utf-8') as f:
        data = f.read()

    for key in oredict:
        data = data.replace(key,oredict[key])

    data = data.replace('\\\n','').replace('  ',' ').splitlines()

    for e in data:
        e = e.strip()
        if len(e) == 0:
            continue
        if e[0] == ';':
            continue

        left,right = e.split('=')
        left = left.strip()
        right = right.strip()
        right = right.split(',')

        outname = translate[left]
        if outname in recipes:
            temp = recipes[outname][0]
        else:
            temp = []

        for inp in right:
            itemcnt = {}
            
            _t = prog.search(inp)
            table = _t.group(1).replace('|','')
            inp = inp[_t.span()[1]:].strip()
            if inp.count('@count') == 0:
                outcnt = 1
            else:
                _t = progcnt.search(inp)
                outcnt = int(_t.group(1))
                inp = inp[:_t.span()[0]]

            inp = inp.replace('@*','').strip()

            inp = inp.split(' ')

            for initem in inp:
                sign,ininame = initem.split(':',1)
                itemcnt[translate[ininame]] = table.count(sign)
            temp.append((itemcnt,outcnt))

        if outname == '生碳网':
            print(temp)
        recipes[outname] = temp,'合成台'

    print('[INFO]合成表 有序合成: %s条'%len(recipes))
    tlrecipes = len(recipes)


    # 读取无序合成表

    with open('./config/无序.ini','r',encoding='utf-8') as f:
        data = f.read()

    for key in oredict:
        data = data.replace(key+' ',oredict[key]+' ')
        data = data.replace(key+'\n',oredict[key]+'\n')

    data = data.replace('\\\n','').replace('  ',' ').splitlines()

    for e in data:
        e = e.strip()
        if len(e) == 0:
            continue
        if e[0] == ';':
            continue

        left,right = e.split('=')
        left = left.strip()
        right = right.strip()
        right = right.split(',')

        outname = translate[left]
        if outname in recipes:
            temp = recipes[outname][0]
        else:
            temp = []

        for inp in right:
            itemcnt = {}
            
            inp = inp.strip()
            if inp.count('@count') == 0:
                outcnt = 1
            else:
                _t = progcnt.search(inp)
                outcnt = int(_t.group(1))
                inp = inp[:_t.span()[0]]

            inp = inp.replace('@*','').strip()

            inp = inp.split(' ')

            for initem in inp:
                ininame = translate[initem]
                if ininame in itemcnt:
                    itemcnt[ininame] += 1
                else:
                    itemcnt[ininame] = 1
            temp.append((itemcnt,outcnt))

        recipes[outname] = temp,'合成台无序'


    print('[INFO]合成表 无序合成: %s条'%(len(recipes)-tlrecipes))
    tlrecipes = len(recipes)

    # 读取高炉合成

    recipes[translate['IC2:itemIngot@3']] = [({translate['minecraft:iron_ingot']:1},1)],\
                                            '高炉'
    recipes[translate['IC2:itemSlag']] = [({translate['minecraft:iron_ingot']:1},1)],\
                                         '高炉'

    print('[INFO]合成表 高炉: %s条'%(len(recipes)-tlrecipes))
    tlrecipes = len(recipes)

    # 读取压缩机合成

    with open('./config/压缩.ini','r',encoding='utf-8') as f:
        data = f.read()

    for key in oredict:
        data = data.replace(key,oredict[key])

    data = data.replace('\\\n','').replace('  ',' ').replace('@-1','')\
           .replace('@0','').splitlines()

    for e in data:
        e = e.strip()
        if len(e) == 0:
            continue
        if e[0] == ';':
            continue

        left,right = e.split('=')
        left = left.strip()
        right = right.strip()

        outname = translate[right]

        left = left[::-1]
        temp1,temp2 = left.split('@',1)
        temp1,temp2 = temp1[::-1],temp2[::-1]
        incnt = int(temp1)
        inname = translate[temp2]

        if outname in recipes:
            ttc = recipes[outname][0]
        else:
            ttc = []
        ttc.append(({inname:incnt},1))

        recipes[outname] = ttc,'压缩机'


    print('[INFO]合成表 压缩机: %s条'%(len(recipes)-tlrecipes))
    tlrecipes = len(recipes)


    # 读取提取机合成表

    with open('./config/提取.ini','r',encoding='utf-8') as f:
        data = f.read()

    for key in oredict:
        data = data.replace(key,oredict[key])

    data = data.replace('\\\n','').replace('  ',' ').splitlines()

    for e in data:
        e = e.strip()
        if len(e) == 0:
            continue
        if e[0] == ';':
            continue

        left,right = e.split('=')
        left = left.strip()
        right = right.strip()

        inp = right
        if inp.count('@count') == 0:
            outcnt = 1
        else:
            _t = progcnt.search(inp)
            outcnt = int(_t.group(1))
            inp = inp[:_t.span()[0]].strip()
        outname = translate[inp]

        itemcnt = {}
        left = left.replace('@*','').strip()
        itemcnt = {translate[left]:1}

        if outname in recipes:
            ttc = recipes[outname][0]
        else:
            ttc = []
        ttc.append((itemcnt,outcnt))

        recipes[outname] = ttc,'提取机'


    print('[INFO]合成表 提取机: %s条'%(len(recipes)-tlrecipes))
    tlrecipes = len(recipes)

    # 读取打粉机合成表

    with open('./config/打粉.ini','r',encoding='utf-8') as f:
        data = f.read()

    for key in oredict:
        data = data.replace(key,oredict[key])

    data = data.replace('\\\n','').replace('  ',' ').splitlines()

    for e in data:
        e = e.strip()
        if len(e) == 0:
            continue
        if e[0] == ';':
            continue

        left,right = e.split('=')
        left = left.strip()
        right = right.strip()

        inp = right
        if inp.count('@count') == 0:
            outcnt = 1
        else:
            _t = progcnt.search(inp)
            outcnt = int(_t.group(1))
            inp = inp[:_t.span()[0]].strip()
        outname = translate[inp]

        itemcnt = {}
        left = left.replace('@*','').strip()
        inp = left
        if inp.count('@count') == 0:
            incnt = 1
        else:
            _t = progcnt.search(inp)
            incnt = _t.group(1)
            inp = inp[:_t.span()[0]].strip()
        itemcnt = {translate[inp]:incnt}

        if outname in recipes:
            ttc = recipes[outname][0]
        else:
            ttc = []
        ttc.append((itemcnt,outcnt))

        recipes[outname] = ttc,'打粉机'


    print('[INFO]合成表 打粉机: %s条'%(len(recipes)-tlrecipes))
    tlrecipes = len(recipes)

    # 读取金属成型机合成

    # 剪切
    recipes[translate['IC2:itemCable@5']] = \
        [({translate[oredict['OreDict:plateIron']]:1},4)],'金属成型机-剪切'
    recipes[translate['IC2:itemCable@10']] = \
        [({translate[oredict['OreDict:plateTin']]:1},3)],'金属成型机-剪切'
    recipes[translate['IC2:itemCable@1']] = \
        [({translate[oredict['OreDict:plateCopper']]:1},3)],'金属成型机-剪切'
    recipes[translate['IC2:itemCable@2']] = \
        [({translate[oredict['OreDict:plateGold']]:1},4)],'金属成型机-剪切'

    # 挤压
    recipes[translate['IC2:itemTinCan']] = \
        [({translate['IC2:itemCasing@1']:1},1)],'金属成型机-挤压'
    recipes[translate['IC2:itemCable@10']] = \
        [({translate[oredict['OreDict:ingotTin']]:1},3)],'金属成型机-挤压'
    recipes[translate['IC2:itemCable@2']] = \
        [({translate['minecraft:gold_ingot']:1},4)],'金属成型机-挤压'
    recipes[translate['IC2:itemRecipePart@12']] = \
        [({translate[oredict['OreDict:blockSteel']]:1},1)],'金属成型机-挤压'
    recipes[translate['IC2:itemCable@1']] = \
        [({translate[oredict['OreDict:ingotCopper']]:1},3)],'金属成型机-挤压'
    recipes[translate['IC2:itemRecipePart@11']] = \
        [({translate['minecraft:iron_block']:1},1)],'金属成型机-挤压'
    recipes[translate['IC2:itemCellEmpty@0']] = \
        [({translate[oredict['OreDict:plateTin']]:1},3)],'金属成型机-挤压'
    recipes[translate['IC2:itemFuelRod']] = \
        [({translate[oredict['OreDict:plateIron']]:1},1)],'金属成型机-挤压'
    recipes[translate['IC2:blockFenceIron']] = \
        [({translate['IC2:itemCasing@4']:1},1)],'金属成型机-挤压'
    recipes[translate['IC2:itemCable@5']] = \
        [({translate['minecraft:iron_ingot']:1},4)],'金属成型机-挤压'

    # 碾压

    recipes[translate['IC2:itemPlates@3']] = \
        [({translate['minecraft:gold_ingot']:1},1)],'金属成型机-挤压'
    recipes[translate['IC2:itemPlates@4']] = \
        [({translate['minecraft:iron_ingot']:1},1)],'金属成型机-挤压'
    recipes[translate['IC2:itemPlates@1']] = \
        [({translate[oredict['OreDict:ingotTin']]:1},1)],'金属成型机-碾压'
    recipes[translate['IC2:itemCasing@6']] = \
        [({translate[oredict['OreDict:plateLead']]:1},2)],'金属成型机-碾压'
    recipes[translate['IC2:itemCasing@5']] = \
        [({translate[oredict['OreDict:plateSteel']]:1},2)],'金属成型机-碾压'
    recipes[translate['IC2:itemCasing@2']] = \
        [({translate[oredict['OreDict:plateBronze']]:1},2)],'金属成型机-碾压'
    recipes[translate['IC2:itemCasing@3']] = \
        [({translate[oredict['OreDict:plateGold']]:1},2)],'金属成型机-碾压'
    recipes[translate['IC2:itemPlates@2']] = \
        [({translate[oredict['OreDict:ingotBronze']]:1},1)],'金属成型机-碾压'
    recipes[translate['IC2:itemCasing@4']] = \
        [({translate[oredict['OreDict:plateIron']]:1},2)],'金属成型机-碾压'
    recipes[translate['IC2:itemPlates@5']] = \
        [({translate[oredict['OreDict:ingotSteel']]:1},1)],'金属成型机-碾压'
    recipes[translate['IC2:itemCasing@0']] = \
        [({translate[oredict['OreDict:plateCopper']]:1},2)],'金属成型机-碾压'
    recipes[translate['IC2:itemPlates']] = \
        [({translate[oredict['OreDict:ingotCopper']]:1},1)],'金属成型机-碾压'
    recipes[translate['IC2:itemPlates@6']] = \
        [({translate[oredict['OreDict:ingotLead']]:1},1)],'金属成型机-碾压'
    recipes[translate['IC2:itemCasing@1']] = \
        [({translate[oredict['OreDict:plateTin']]:1},2)],'金属成型机-碾压'

    print('[INFO]合成表 金属成型机: %s条'%(len(recipes)-tlrecipes))
    tlrecipes = len(recipes)

    # 读取高级太阳能合成表

    with open('./config/高级太阳能.ini','r',encoding='utf-8') as f:
        data = f.read()

    for key in oredict:
        data = data.replace(key,oredict[key])

    data = data.replace('\\\n','').replace('  ',' ').splitlines()

    for e in data:
        e = e.strip()
        if len(e) == 0:
            continue
        if e[0] == ';':
            continue

        left,right = e.split('=')
        left = left.strip()
        right = right.strip()
        right = right.split(',')

        outname = translate[left]
        if outname in recipes:
            temp = recipes[outname][0]
        else:
            temp = []

        for inp in right:
            itemcnt = {}
            
            _t = prog.search(inp)
            table = _t.group(1).replace('|','')
            inp = inp[_t.span()[1]:].strip()
            if inp.count('@count') == 0:
                outcnt = 1
            else:
                _t = progcnt.search(inp)
                outcnt = int(_t.group(1))
                inp = inp[:_t.span()[0]]

            inp = inp.replace('@*','').strip()

            inp = inp.split(' ')

            for initem in inp:
                sign,ininame = initem.split(':',1)
                itemcnt[translate[ininame]] = table.count(sign)
            temp.append((itemcnt,outcnt))

        if outname == '生碳网':
            print(temp)
        recipes[outname] = temp,'合成台'

    print('[INFO]合成表 高级太阳能: %s条'%(len(recipes)-tlrecipes))
    tlrecipes = len(recipes)


    # 附加规则
    recipes['青铜锭'] = [({'青铜粉':1},1)],'熔炉'
    recipes['青铜粉'] = ([({'锡粉': 1, '铜粉': 3}, 4)], '合成台')
    recipes['铜粉'] = ([({'铜锭': 1}, 1)], '合成台')
    recipes['锡粉'] = ([({'锡锭': 1}, 1)], '合成台')
    recipes['铁粉'] = ([({'铁锭': 1}, 1)], '合成台')
    recipes['铅粉'] = ([({'铅锭': 1}, 1)], '合成台')
    recipes['青金石粉'] = ([({'青金石': 1}, 1)], '合成台')
    recipes['防爆石'] = ([({'铁质脚手架':1,'建筑泡沫':1},1)],'建筑泡沫喷枪')
    
    print('[INFO]合成表 其他: %s条'%(len(recipes)-tlrecipes))


    with open('raw.ini','r',encoding='utf-8') as f:
        raw = f.read().splitlines()

    while raw.count(''):
        del raw[raw.index('')]

    print('[INFO]载入原材料规则: %s条'%(len(raw)))

    print('================载入完毕================\n')

    while True:
        start = input('目标产物全称(输入quit退出):')
        if start=='quit':
            break

        lst = {start:1}
        flag = True
        dopath = []
        ret = {}

        while flag:
            newlst = {}
            for key in lst:
                if key not in recipes or key in raw: # 最终产物
                    if key in ret:
                        ret[key] += lst[key]
                    else:
                        ret[key] = lst[key]
                else: # 继续细分
                    way = recipes[key][0][0]
                    outcnt = way[1]
                    ins = way[0]
                    temp = {}
                    for item in ins:
                        temp[item] = math.ceil(lst[key]/outcnt)*ins[item]
                        if item in newlst:
                            newlst[item] += math.ceil(lst[key]/outcnt)*ins[item]
                        else:
                            newlst[item] = math.ceil(lst[key]/outcnt)*ins[item]
                    if inlst(dopath, key, lambda x:x[0][0]) == -1:
                        dopath.insert(0,[[key,outcnt*math.ceil(lst[key]/outcnt)],temp])
                    else:
                        index = inlst(dopath, key, lambda x:x[0][0])
                        dopath[index][0][1] += outcnt*math.ceil(lst[key]/outcnt)
                        for kk in temp:
                            dopath[index][1][kk] += temp[kk]
            lst = newlst
            if len(lst) == 0:
                flag = False


        print('(合成路线功能目前尚不稳定，内容仅供参考)\n合成路线:')
        for each in dopath:
            outprint = []
            for kk in each[1]:
                outprint.append('%s*%s'%(kk,each[1][kk]))
            print('\t',' + '.join(outprint),'=>','%s*%s'%(each[0][0],each[0][1]))
        print('\n总耗材:')
        for kk in ret:
            zutext = ''
            if ret[kk] >= 64:
                if ret[kk]%64:
                    zutext = '(%s组 %s个)'%(ret[kk]//64,ret[kk]%64)
                else:
                    zutext = '(%s组)'%(ret[kk]//64)
            print('\t%s: %s%s'%(kk,ret[kk],zutext))
        print('========================================\n')

    system('pause')


if __name__ == '__main__':
    try:
        main()
    except BaseException as e:
        print('\n\n==========程序发生意外错误==========')
        traceback.print_exc()
        print('请将此内容截图发送至开发者\n')
        system('pause')
        sys.exit(1)
