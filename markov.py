#!/usr/bin/python

import numpy
import scipy
import sys
import midi
import csv
import re
from random import randint
import matplotlib.pyplot as plt

	



def main():

	filename = sys.argv[1]
	aubio_out = open(filename, 'r')
	n = aubio_out.readlines()
	midilist = []
	ad = 1
	tick_val = .0023
	numpy.set_printoptions(threshold='nan')

	# reads through aubionotes txt file and extracts pitch and duration information. 
	# rejects notes shorter than 55 ticks
	# Makes midilist. format: pitch, start time, end time
	for x in range(5,len(n)-3):
		current_line = n[x]
		match = re.search(r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', current_line)
		if match:
			tick = int((float(match.group(3)) - float(match.group(2)))/tick_val)
			if(tick>55):
				midilist.append((int((float)(match.group(1))),tick))

	makemidi(midilist, 0) 
	makemarkov(midilist)



def makemidi(midilist, write):
	# General midi business
	pattern = midi.Pattern()
	track = midi.Track()
	pattern.append(track)
	tempo = 59
	tick_val = (60*1000000)/tempo
	tick_val = float(tick_val/220000000)
	flag = 0
	ticks = []
		

	for n in range(0, len(midilist)-1):
		pitch1 = int(midilist[n][0])
		nextpitch = int(midilist[n+1][0])
		off_tick = midilist[n][1]
		ticks.append(off_tick)
		on = midi.NoteOnEvent(tick = 0, velocity = 100, pitch = pitch1)
		track.append(on)
		off = midi.NoteOffEvent(tick = off_tick, pitch = pitch1)
		track.append(off)

	eot = midi.EndOfTrackEvent(tick = 1)
	track.append(eot)
	# Writes file to disk if wanted
	if write == 1:
		midi.write_midifile("bday.mid", pattern)
	#print("Once")
	#print(ticks)
	




def makemarkov(midilist):
	size = len(midilist)
	pitchmodel = numpy.zeros((144,12))
	count = 0
	firstnotes = [(midilist[0][0]%12),(midilist[1][0]%12)]
	durations = [110, 220, 330, 440, 550, 660, 770, 880, 990, 1100, 1210, 1320, 1430, 1540, 1650, 1760]
	oneback = firstnotes[1]
	twoback = firstnotes[0]
	for x in range(2,size-2):
		if midilist[x][1] > 55:
			a = midilist[x][0]%12
			pitchmodel[(twoback*12)+oneback][a] += 1
			twoback = oneback
			oneback = a

			

	#Generates duration markov model and sets any durations less than a 16th note to 0
	durationmodel = numpy.zeros((16,16))
	lengths = []
	last = 0

	for x in range(2,size-2):
		list1 = []
		if midilist[x][1] < durations[0]:
			continue

		#quantizes each tick in "ticks" to one of the above values in durations
		#gets difference between actual value and each quantization value, then uses index of min 
		for xx in range(0, 15):
			this = abs(midilist[x][1] - durations[xx])
			list1.append(this)
		n = durations[list1.index(min(list1))]

		if last != 0:
			durationmodel[last][n/110] += 1
		lengths.append(n)
		last = n/110
	firstduration = lengths[0]


	#print(len(lengths))
	print("")
	print("")
	#print(len(midilist))
	generatemarkov(pitchmodel, durationmodel, firstnotes, firstduration)







def generatemarkov(pitchmodel, durationmodel, firstnote, firstduration):

	# num_notes is number of note/duration pairs generated
	# gets sum of chosen row in the model, generates random number in range of sum, then iterates through indexes until
	# it finds the next note.
	#to enforce pitch shifts, add 48 for each
	num_notes = 6000
	lastpair = (firstnote[0]*12) + firstnote[1]
	notelust = []
	lagger = firstnote[1]
	chosen = 0
	notelust.append(firstnote[0]+48)
	notelust.append(firstnote[1]+48)


	for x in range(0,num_notes - 2):
		print(x)

		rowsum = pitchmodel[lastpair].sum()
		if rowsum != 0:
			random = randint(1, rowsum)
			runningsum = random
			print("Rowsum: ", rowsum)
			print("running: ", runningsum)
			for num in range(0,12):
				runningsum = runningsum - pitchmodel[lastpair][num]
				if runningsum <= 0:
					chosen = num
					notelust.append(chosen+48)
					lastpair = (lagger*12) + chosen
					lagger = chosen
					break
		else:
			chosen = randint(0,11) 

			print("")
			print("")
			notelust.append(chosen+48)
			lastpair = (lagger*12) + chosen
			lagger = chosen



	lastdur = firstduration/110
	durlust = []
	durlust.append(lastdur*110)

	for x in range(0,num_notes-1):
		dur_rowsum = durationmodel[lastdur].sum()
		if dur_rowsum != 0:
			random = randint(1, dur_rowsum)
			dur_runningsum = random
			for num in range(0,15):
				dur_runningsum = dur_runningsum - durationmodel[lastdur][num]
				if dur_runningsum <= 0:
					lastdur = num
					durlust.append(lastdur*110)
					break
				if num == 15:
					lastdur = randint(0,15)
					durlust.append(lastdur*110)
		else:
			lastdur = randint(0,15)
			durlust.append(lastdur*110)

#	file = open("lame.csv", "wb")
#	john = open("lamer.csv", "wb")

#	for h in range (0, num_notes-2):
#		file.write(str(notelust[h]))
#		john.write(str(durlust[h]))
#		if h < num_notes-3:
#			file.write(", ")
#			john.write(", ")

#	file.close()



	gen_result = zip(notelust, durlust)
	last_list = gen_result
	makemidi(gen_result, 1)
	return(last_list)






def updatemodels(pitchmodel, durationmodel, positive_start, positive_end, negative_start, negative_end, last_list)
	














if __name__ == "__main__":
    main()