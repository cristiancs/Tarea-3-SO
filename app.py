#!/usr/bin/python3
# -*- coding: utf-8 -*-

import threading
import time
import queue

# SETTINGS

cargas_papel = 10
log_console = False

# BD de la Aplicación

casilleros = [0,0,0,0,0,0,0,0,0,0];
papel_casilleros = [];
for x in range(0,10):
	papel_casilleros.append(cargas_papel)
cola_casilleros = queue.Queue()
cola_lavamanos = queue.Queue()
cola_secador = queue.Queue()
alumnos = {};
lavamanos = [0,0,0,0,0];
secador = [0,0];
count_alumnos = 0;
count_threads = 0;
casilleros_semaforo = threading.BoundedSemaphore();
papel_casilleros_semaforo = threading.BoundedSemaphore();
lavamos_semaforo = threading.BoundedSemaphore();
secador_semaforo = threading.BoundedSemaphore();
alumnos_file_semaforo = threading.BoundedSemaphore();
aseo_file_semaforo = threading.BoundedSemaphore();
alumnos_file = open("clientes.txt","w")
aseo_file = open("personal.txt","w")


def procesar_alumnos():
	global alumnos, count_alumnos, count_threads, crono
	start = count_threads
	texto = ""
	if(count_threads == 0):
		texto = "Ingrese la cantidad de Alumnos: "
	read = int(input(texto));
	
	while read > 25 or count_alumnos+read > 25:
		print("La cantidad de alumnos ejecutandose no pueder ser mayor a 25. Actualmente hay "+str(count_alumnos))
		read = int(input("Ingrese la cantidad de Alumnos: "));
	if read == -1:
		return False
	if(count_threads == 0):
		crono.start()
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
		self.time = -1;
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
		global papel_casilleros, papel_casilleros_semaforo, cargas_papel, crono, log_console
		threading.Thread.__init__(self)
		self.papel_casilleros = papel_casilleros
		self.papel_casilleros_semaforo = papel_casilleros_semaforo
		self.cola = queue.Queue()
		self.cargas_papel = cargas_papel
		self.crono = crono
		self.pararVar = False
		self.aseo_file = aseo_file
		self.aseo_file_semaforo = aseo_file_semaforo
		self.log_console = log_console
	def parar(self):
		self.pararVar = True
	def log(self, text):
		respuesta = str(self.crono.getPretty())+": Aseo "+text
		
		self.aseo_file_semaforo.acquire()
		self.aseo_file.write(respuesta+"\n")
		self.aseo_file_semaforo.release()
		if self.log_console:
			print(respuesta)
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
		global casilleros, casilleros_semaforo ,lavamos_semaforo ,secador_semaforo, cola_casilleros, crono, papel_casilleros, aseo, papel_casilleros_semaforo, cola_lavamanos, cola_secador, lavamanos, secador, alumnos_file_semaforo, log_console
		threading.Thread.__init__(self)
		self.casilleros = casilleros;
		self.lavamanos = lavamanos
		self.secador = secador
		self.casilleros_semaforo = casilleros_semaforo
		self.lavamos_semaforo = lavamos_semaforo
		self.secador_semaforo = secador_semaforo
		self.cola_casilleros = cola_casilleros
		self.papel_casilleros = papel_casilleros
		self.papel_casilleros_semaforo = papel_casilleros_semaforo
		self.cola_lavamanos = cola_lavamanos
		self.cola_secador = cola_secador
		self.number = number;
		self.micasillero = -1;
		self.crono = crono
		self.aseo = aseo
		self.alumnos_file = alumnos_file
		self.alumnos_file_semaforo = alumnos_file_semaforo
		self.log_console = log_console
	def log(self, text):
		respuesta = str(self.crono.getPretty())+": Alumno "+str(self.number+1)+" "+text

		self.alumnos_file_semaforo.acquire()
		self.alumnos_file.write(respuesta+"\n")
		self.alumnos_file_semaforo.release()

		if self.log_console:
			print(respuesta)
	def run(self): 
		self.verificar_casillero()


	# GESTION CASILLEROS

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
		# self.log("Intenta entrar al casillero")	
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
		self.casilleros_semaforo.acquire()
		self.casilleros[self.micasillero] = 0
		self.log("Sale del casillero "+str(self.micasillero))
		self.casilleros_semaforo.release()
		self.verificar_lavamanos()





	# GESTION LAVAMANOS

	def entrar_lavamanos(self):
		counter = 0
		self.lavamos_semaforo.acquire()
		while self.micasillero == -1 and counter < 5:
			if(self.lavamanos[counter] == 0):
				# Casillero Libre
				self.log("Utiliza lavamanos " +str(counter))

				self.lavamanos[counter] = 1
				self.micasillero = counter
				self.cola_lavamanos.get()
				self.lavamos_semaforo.release()
				time.sleep(5)
				self.salir_lavamanos()
				return True
			counter+=1
		self.lavamos_semaforo.release()
		return False
	def salir_lavamanos(self):
		self.lavamos_semaforo.acquire()
		self.lavamanos[self.micasillero] = 0
		self.log("Sale del lavamano "+str(self.micasillero))
		self.lavamos_semaforo.release()
		self.verificar_secador()
	def verificar_lavamanos(self):
		self.micasillero = -1 
		# self.log("Intenta utilizar el lavamanos")	
		# Agregar a la cola
		self.cola_lavamanos.put(self.number);
		while self.cola_lavamanos.queue[0] != self.number:
			# No somos los primeros de la cola, lo intentamos en 1 segundo
			time.sleep(.1)
		
		# Somos los primeros de la cola, intentamos entrar
		entro = self.entrar_lavamanos()
		while not entro:
			time.sleep(.1)
			entro = self.entrar_lavamanos()


	# GESTION SECADOR

	def entrar_secador(self):
		counter = 0
		self.secador_semaforo.acquire()
		while self.micasillero == -1 and counter < 2:
			if(self.secador[counter] == 0):
				# Casillero Libre
				self.log("Utiliza secador " +str(counter))

				self.secador[counter] = 1
				self.micasillero = counter
				self.cola_secador.get()
				self.secador_semaforo.release()
				time.sleep(5)
				self.salir_secador()
				return True
			counter+=1
		self.secador_semaforo.release()
		return False
	def salir_secador(self):
		self.lavamos_semaforo.acquire()
		self.secador[self.micasillero] = 0
		self.log("Sale del secador "+str(self.micasillero))
		self.lavamos_semaforo.release()
		alumno_sale()
	def verificar_secador(self):
		self.micasillero = -1 
		# self.log("Intenta usar secador")	
		# Agregar a la cola
		self.cola_secador.put(self.number);
		while self.cola_secador.queue[0] != self.number:
			# No somos los primeros de la cola, lo intentamos en 1 segundo
			time.sleep(.1)
		
		# Somos los primeros de la cola, intentamos entrar
		entro = self.entrar_secador()
		while not entro:
			time.sleep(.1)
			entro = self.entrar_secador()


		
	



crono = Crono();
aseo = Aseo();

print("Durante la ejecución del programa podrá ingresar un número seguido de enter para agregar más alumnos, o -1 para salir.")

aseo.start();

while procesar_alumnos():
	continue



# Wait for threads to end
for key, thread in alumnos.items():
	 thread.join()

aseo.parar()
crono.parar()

aseo.join()
crono.join()

aseo_file.close()
alumnos_file.close()
print ("Gracias por Utilizar el Programa")