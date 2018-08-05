import queue

q = queue.Queue()

for i in range(5):
    q.put("hola"+str(i))
print(q.queue[0])
while not q.empty():
    print(q.get(), end=' ')
print()
