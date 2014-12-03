#!/usr/bin/python
# coding=utf-8

import sys
from lista_ordenada import ListaOrdenada


class NoExisteTareaAnterior(Exception):
    pass


class TiempoInicialNegativo(Exception):
    pass


class Tarea:

    def __init__(self, id, tiempo, beneficio, vencimiento):
        self.id = id
        self.tiempo = tiempo
        self.beneficio = beneficio
        self.vencimiento = vencimiento

    def __cmp__(self, other):
        if self.vencimiento < other.vencimiento:
            return -1
        if self.vencimiento > other.vencimiento:
            return 1
        return 0

    def __str__(self):
        return '%s(d=%s, b=%s, v=%s)' % (self.id, self.tiempo, self.beneficio,
                self.vencimiento)

class TP3:

    def __init__(self, lines):
        """
        O(n*log(n))
        n: len(lines)
        """
        id = 0
        self.tareas = ListaOrdenada(permitir_repetidos=True) # O(1)
        for line in lines: # len(lines)
            line = line.strip() # O(1)
            if line == "":
                continue
            tiempo, beneficio, vencimiento = line.split(',') # O(1)
            id += 1
            tiempo = int(tiempo)
            beneficio = float(beneficio)
            vencimiento = int(vencimiento)
            tarea = Tarea(id, tiempo, beneficio, vencimiento) # O(1)
            self.tareas.insert(tarea) # O(log(len(self.tareas)))

    def indices_tareas(self):
        return range(len(self.tareas))

    def d(self, i):
        """
        Duración de la tarea i
        """
        return self.tareas[i].tiempo

    def b(self, i, t):
        """
        Beneficio de la tarea i si finaliza en el instante t.
        """
        if t > self.tareas[i].vencimiento:
            return 0
        return self.tareas[i].beneficio

    def t_inicial(self, t_final, i):
        """
        Instante inicial de la tarea i si finaliza en el instante t_final
        """
        t_inicial = t_final - self.d(i)
        if t_inicial < 0:
            raise TiempoInicialNegativo()
        return t_inicial

    def tarea_anterior(self, i):
        """
        Obtiene la tarea anterior a la tarea i.
        """
        if i == 0:
            raise NoExisteTareaAnterior()
        return i-1

    def ultima_tarea(self):
        return len(self.tareas)-1

    def ultimo_vencimiento(self):
        return self.tareas[self.ultima_tarea()].vencimiento

    def resolver(self):
        """
        O(W*n)
        W: Último vencimiento
        n: Cantidad de tareas
        Obtiene la planificación óptima y su beneficio.
        Devuelve la tupla (planificacion, resto, beneficio)
        """

        M = []
        # O(W*n)
        for t in xrange(0,self.ultimo_vencimiento()+1): # W+1
            M.append([])
            for i in self.indices_tareas(): # n
                M[t].append(0)

        for t in xrange(1,self.ultimo_vencimiento()+1): # W+1
            for i in self.indices_tareas(): # n
                try:
                    try:
                        M[t][i] = max(M[self.t_inicial(t,i)][self.tarea_anterior(i)]+self.b(i,t),
                                M[t][self.tarea_anterior(i)]) # O(1)
                    except TiempoInicialNegativo:
                        M[t][i] = M[t][self.tarea_anterior(i)] # O(1)
                except NoExisteTareaAnterior:
                    try:
                        M[t][i] = max(M[self.t_inicial(t,i)][i], self.b(i,t)) #(1)
                    except TiempoInicialNegativo:
                        pass

        t = self.ultimo_vencimiento()
        i = self.ultima_tarea()
        planificacion = []
        planificada = [False for i in self.indices_tareas()]

        # O(W+n)
        while t>=0:
            try:
                # Si en el tiempo t para la tarea i el beneficio es mayor que
                # el beneficio en el tiempo t de la tarea anterior, entonces la tarea i
                # está incluida en la planificación.
                if M[t][i] > M[t][self.tarea_anterior(i)]:
                    planificacion.insert(0,i)
                    planificada[i] = True
                    t=self.t_inicial(t,i)
                    i=self.tarea_anterior(i)
                # Sino, si en el tiempo t-1 la tarea i tiene mayor beneficio que
                # en el tiempo t de la tarea anterior, entonces decrementamos t
                # en una una unidad
                elif M[t-1][i] > M[t][self.tarea_anterior(i)]:
                    t = t - 1
                # Sino, significa que la tarea i no está incluida en la planificación
                # y vamos a la tarea anterior.
                else:
                    i = self.tarea_anterior(i)
            except NoExisteTareaAnterior:
                # En caso que no exista tarea anterior, significa que estamos en la primer
                # tarea, por tanto, en caso que el beneficio sea mayor a 0, entonces indica
                # que la primer tarea está incluida en la planificación.
                if M[t][i]>0:
                    planificacion.insert(0,i)
                    planificada[i] = True
                break

        resto = set()
        # O(n)
        for i in self.indices_tareas():
            if not planificada[i]:
                resto.add(self.tareas[i].id)

        # O(n)
        return ([self.tareas[i].id for i in planificacion], resto, 
                M[self.ultimo_vencimiento()][self.ultima_tarea()])


import unittest


class TP3TestCase(unittest.TestCase):

    def test_init(self):
        """
        Formato de línea: duración, beneficio, vencimiento
        """
        tp3 = TP3([
            '1,2,3',
            '1,1,1',
            '2,2,2',
            '1,0,1',
            ])

        self.assertEqual(len(tp3.tareas), 4)
        self.assertEqual(tp3.ultimo_vencimiento(),3)

    def test_va_todo(self):
        """
        Formato de línea: duración, beneficio, vencimiento
        """
        tp3 = TP3([
            '1,1,1',
            '1,3,2',
            '2,2,4',
            '3,1,7',
            ])

        self.assertEqual(tp3.ultimo_vencimiento(),7)
        planificacion, resto, beneficio = tp3.resolver()

        self.assertEqual(beneficio, 7.0)
        self.assertEqual(planificacion,[1,2,3,4])
        self.assertEqual(resto,set())

    def test_cero_beneficio(self):
        """
        Formato de línea: duración, beneficio, vencimiento
        """
        tp3 = TP3([
            '3,1,2',
            '4,3,1',
            '3,2,1',
            '5,1,2',
            ])

        self.assertEqual(tp3.ultimo_vencimiento(),2)
        planificacion, resto, beneficio = tp3.resolver()

        self.assertEqual(beneficio, 0.0)
        self.assertEqual(planificacion,[])
        self.assertEqual(resto,set([1,2,3,4]))

    def test_poderoso_el_chiquitin(self):
        """
        Formato de línea: duración, beneficio, vencimiento
        """
        tp3 = TP3([
            '7,4,8',
            '7,4,8',
            '2,5,8',
            '7,4,8',
            ])

        self.assertEqual(tp3.ultimo_vencimiento(),8)
        planificacion, resto, beneficio = tp3.resolver()

        self.assertEqual(beneficio, 5.0)
        self.assertEqual(planificacion,[3])
        self.assertEqual(resto,set([1,2,4]))


def procesar():
    for filepath in sys.argv[1:]:
        with open(filepath) as f:
            tp3 = TP3(f.readlines())
            tp3.resolver()


if __name__ == '__main__':
    if len(sys.argv) == 1:
        unittest.main()
    else:
        procesar()


