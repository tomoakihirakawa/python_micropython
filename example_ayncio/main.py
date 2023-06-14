import time
import asyncio

# -------------------------------------------------------- #

#すこし眠って終わる意味のない関数
async def process(name, sec):
    print(f'\nstart {name}')
    await asyncio.sleep(sec)
    print(f'end {name}')
    return f'{name}/{sec}'
#この関数の並列実行をチェックする

# -------------------------------------------------------- #

#意味のないprocess関数を一つ一つ実行する関数
async def syn_function():
    print(await process('A', 1))
    print(await process('B', 1))
    print(await process('C', 1))
        
#意味のないprocess関数をスケジューリングして，一気に実行する関数
async def asyn_function():
    A = asyncio.create_task(process('A',1))
    B = asyncio.create_task(process('B',1))
    C = asyncio.create_task(process('C',1))        
    print(await A)
    print(await B)
    print(await C)    
    
# -------------------------------------------------------- #

start = time.time()

#このようにrunとして実行する関数をエントリーポイントと呼ぶ
#関数には，一気に実行したい複数の関数が入っている
asyncio.run(syn_function())

end = time.time()
print(f'process time: {end - start}')