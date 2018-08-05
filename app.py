#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
import time
import queue
exitFlag = 0


# BD de la Aplicación
cargas_papel = 1
casilleros = [0,0,0,0,0,0,0,0,0,0];
papel_casilleros = [];
for x in range(0,10):
	papel_casilleros.append(cargas_papel)
cola_casilleros = queue.Queue()
alumnos = {};
lavamos = [0,0,0,0,0];
secador = [0,0];
count_alumnos = 0;
count_threads = 0;
casilleros_semaforo = threading.BoundedSemaphore();
papel_casilleros_semaforo = threading.BoundedSemaphore();
lavamos_semaforo = threading.BoundedSemaphore();
secador_semaforo = threading.BoundedSemaphore();

def procesar_alumnos():
	global alumnos, count_alumnos, count_threads
	start = count_threads
	read = int(input("Ingrese la cantidad de Alumnos: "));
	while read > 25 or count_alumnos+read > 25:
		print("La cantidad de alumnos ejecutandose no pueder ser mayor a 25. Actualmente hay "+str(count_alumnos))
		read = int(input("Ingrese la cantidad de Alumnos: "));
	if read == -1:
		return False
	for x in range(0, read):
		alumnos[count_threads] = Alumno(count_threads);
		alumnos[count_threads].start();
		count_alumnos+=1;
		count_threads+=1;
		
		
	return (start, read)

def alumno_sale():
	global count_alumnos
	count_alumnos-=1

class Crono (threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		self.time = 0;
		self.pararVar = False
	def parar(self):
		self.pararVar = True
	def getPretty(self):
		minutos = int(self.time/60)
		segundos = int(self.time%60)
		if len(str(segundos)) == 1:
			segundos = "0"+str(segundos)
		else:
			segundos = str(segundos)
		if len(str(minutos)) == 1:
			minutos = "0"+str(minutos)
		else:
			minutos = str(minutos)
		return "["+minutos+":"+segundos+"]"
	def run(self): 
		while not self.pararVar:
			self.time+=1;
			time.sleep(1);
class Aseo (threading.Thread):
	def __init__(self):
		global papel_casilleros, papel_casilleros_semaforo, cargas_papel, crono
		threading.Thread.__init__(self)
		self.papel_casilleros = papel_casilleros
		self.papel_casilleros_semaforo = papel_casilleros_semaforo
		self.cola = queue.Queue()
		self.cargas_papel = cargas_papel
		self.crono = crono
		self.pararVar = False
	def parar(self):
		self.pararVar = True
	def log(self, text):
		respuesta = str(self.crono.getPretty())+": Aseo "+text
		print(respuesta);
	def reponer(self, ubicacion):
		self.cola.put(ubicacion)
	def run(self): # Call it with var.start();
		while not self.pararVar:
			while not self.cola.empty():
				self.papel_casilleros_semaforo.acquire()
				elem = self.cola.get()
				self.log("Repone papel de "+str(elem))
				self.papel_casilleros[elem] = self.cargas_papel
				self.papel_casilleros_semaforo.release()
			time.sleep(0.01)
		self.log("Termina")

class Alumno (threading.Thread):
	def __init__(self, number):
		global casilleros, casilleros_semaforo ,lavamos_semaforo ,secador_semaforo, cola_casilleros, crono, papel_casilleros, aseo, papel_casilleros_semaforo
		threading.Thread.__init__(self)
		self.casilleros = casilleros;
		self.casilleros_semaforo = casilleros_semaforo
		self.lavamos_semaforo = lavamos_semaforo
		self.secador_semaforo = secador_semaforo
		self.cola_casilleros = cola_casilleros
		self.papel_casilleros = papel_casilleros
		self.papel_casilleros_semaforo = papel_casilleros_semaforo
		self.step = 0;
		self.number = number;
		self.micasillero = -1;
		self.crono = crono
		self.aseo = aseo
	def log(self, text):
		respuesta = str(self.crono.getPretty())+": Alumno "+str(self.number+1)+" "+text
		print(respuesta);
	def entrar_casillero(self):
		counter = 0
		self.casilleros_semaforo.acquire()

		while self.micasillero == -1 and counter < 10:
			if(self.casilleros[counter] == 0):
				# Casillero Libre
				self.papel_casilleros_semaforo.acquire()
				self.log("Ingresa al casillero " +str(counter))

				# Revisar si hay papel
				if self.papel_casilleros[counter] == 0:
					# No hay papel, liberamos los recursos y nos vamos a esperar
					self.log("solicita papel para "+str(counter))
					self.aseo.reponer(counter)
					self.casilleros_semaforo.release()
					self.papel_casilleros_semaforo.release()
					return False
				else:
					self.papel_casilleros[counter]-=1
					self.papel_casilleros_semaforo.release()
				self.log("Utiliza casillero "+str(counter))
				self.casilleros[counter] = 1
				self.micasillero = counter
				self.cola_casilleros.get()
				self.casilleros_semaforo.release()
				time.sleep(5)
				self.salir_casillero()
				return True
			counter+=1
		self.casilleros_semaforo.release()
		return False
	def verificar_casillero(self):
		self.step = 1;
		self.log("Intenta entrar al casillero")	
		# Agregar a la cola
		self.cola_casilleros.put(self.number);
		while self.cola_casilleros.queue[0] != self.number:
			# No somos los primeros de la cola, lo intentamos en 1 segundo
			time.sleep(.1)
		
		# Somos los primeros de la cola, intentamos entrar
		entro = self.entrar_casillero()
		while not entro:
			time.sleep(.1)
			entro = self.entrar_casillero()

	def salir_casillero(self):
		self.step = 2;
		self.casilleros_semaforo.acquire()
		self.casilleros[self.micasillero] = 0
		self.log("Sale del casillero "+str(self.micasillero))
		self.casilleros_semaforo.release()

		
	def run(self): # Call it with var.start();
		self.verificar_casillero()
		alumno_sale()
		#self.log("finaliza sus operaciones")



crono = Crono();
aseo = Aseo();

print("Durante la ejecución del programa podrá ingresar un número seguido de enter para agregar más alumnos, o -1 para salir.")

aseo.start();
crono.start()

while procesar_alumnos():
	continue


# Wait for threads to end
for key, thread in alumnos.items():
	 thread.join()

aseo.parar()
crono.parar()

aseo.join()
crono.join()
print ("Gracias por UTilizar el Programa")