#!/usr/bin/python

import numpy
from scipy.io import wavfile
import sys
import midi
import csv
import wave, struct
import re
from random import randint



class system:

	def __init__(self, audiofile, tracker, midi_in, pitch_list, duration_list, time_list, p_model, d_model, first_pitches, first_d, gen_result):
		self.audiofile = audiofile
		self.tracker = tracker
		self.midi_in = midi_in
		self.pitch_list = pitch_list
		self.duration_list = duration_list
		self.time_list = time_list
		self.p_model = p_model
		self.d_model = d_model
		self.first_pitches = first_pitches
		self.first_d = first_d
		self.gen_result = gen_result

	def makemidi(self):
		# General midi business
		pattern = midi.Pattern()
		track = midi.Track()
		pattern.append(track)
		tempo = 59
		tick_val = (60*1000000)/tempo
		tick_val = float(tick_val/220000000)
		ticks = []

		for n in range(0, len(self.midi_in)-1):
			pitch1 = int(self.midi_in[n][0])
			nextpitch = int(self.midi_in[n+1][0])
			off_tick = self.midi_in[n][1]
			ticks.append(off_tick)
			on = midi.NoteOnEvent(tick = 0, velocity = 100, pitch = pitch1)
			track.append(on)
			off = midi.NoteOffEvent(tick = off_tick, pitch = pitch1)
			track.append(off)

		eot = midi.EndOfTrackEvent(tick = 1)
		track.append(eot)
		# Writes file to disk if wanted

		midi.write_midifile("bday.mid", pattern)

	def makemarkov(self):
		size = len(self.midi_in)
		self.p_model = numpy.zeros((144,12))
		count = 0
		firstnotes = [(self.midi_in[0][0]%12),(self.midi_in[1][0]%12)]
		durations = [110, 220, 330, 440, 550, 660, 770, 880, 990, 1100, 1210, 1320, 1430, 1540, 1650, 1760]
		oneback = firstnotes[1]
		twoback = firstnotes[0]
		self.tracker = [[] for _ in range(12)]

		self.tracker[twoback%12].append(0)
		self.tracker[oneback%12].append(1)

		for x in range(2,size-2):
			a = self.midi_in[x][0]%12
			self.tracker[a].append(x)
			self.p_model[(twoback*12)+oneback][a] += 1
			twoback = oneback
			oneback = a


		#Generates duration markov model and sets any durations less than a 16th note to 0
		self.d_model = numpy.zeros((16,16))
		lengths = []
		last = 0

		for x in range(2,size-2):
			list1 = []
			if self.midi_in[x][1] < durations[0]:
				continue

			#quantizes each tick in "ticks" to one of the above values in durations
			#gets difference between actual value and each quantization value, then uses index of min
			for xx in range(0, 15):
				this = abs(self.midi_in[x][1] - durations[xx])
				list1.append(this)
			n = durations[list1.index(min(list1))]

			if last != 0:
				self.d_model[last][n/110] += 1
			lengths.append(n)
			last = n/110
		self.first_d = lengths[0]
		self.first_pitches = firstnotes

	def generatemarkov(self):

		# num_notes is number of note/duration pairs generated
		# gets sum of chosen row in the model, generates random number in range of sum, then iterates through indexes until
		# it finds the next note.
		#to enforce pitch shifts, add 48 for each
		num_notes = 600
		lastpair = (self.first_pitches[0]*12) + self.first_pitches[1]
		notelust = []
		lagger = first_pitches[1]
		chosen = 0
		tmelist = []
		notelust.append(self.first_pitches[0]+48)
		notelust.append(self.first_pitches[1]+48)


		for x in range(0,num_notes - 2):
			print(x)

			rowsum = self.p_model[lastpair].sum()
			if rowsum != 0:
				random = randint(1, rowsum)
				runningsum = random

				for num in range(0,12):
					runningsum = runningsum - self.p_model[lastpair][num]
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


		self.pitch_list = notelust
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
			if x == 0:
				timelist.append(0, lastdur*110*tick_val)
			else:
				timelist.append(timelist[x-1][2], lastdur*110*tick_val)


		self.duration_list = durlust
		self.time_list = timelist
		self.gen_result = zip(notelust, durlust)
		self.makemidi()

	def updatemodels(pitchmodel, durationmodel, pairlists, timelist, notes, durations):
		# changes the good ones
		start_index = 0
		end_index = 0
		for h in range (0, len(pairlists[0])):
			start_time = pairlists[0][h][1]
			end_time = pairlists[0][h][2]
			flag = 0
			for j in range (0, len(timelist)):
				if self.time_list[j[1]] > start_time and flag == 0:
					start_index = j-1
					flag = 1
				if self.time_list[j][1] > end_time:
					end_index = j-1
			for x in range(0,):
				if self.midi_in[x][1] > 55:
					a = self.midi_in[x][0]%12
					p_model[(twoback*12)+oneback][a] += 1
					twoback = oneback
					oneback = a

	#def slice(self):

	def parsemidi(aubionotes,snd):
		# reads through aubionotes txt file and extracts pitch and duration information.
		# merges notes shorter than 150ms with previous note
		# Populates midi_in & audiofile. format: pitch, start time, end time
		n = aubionotes
		merge = 0
		for x in range(4,len(n)-3):
			if (merge == 0):
				curr_line = n[x]
				curr_match = re.search(r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', curr_line)
				if curr_match:
					curr_pitch = curr_match.group(1)
					curr_start = curr_match.group(2)
					curr_end = curr_match.group(3)
					#print str(x) + " " + str(curr_pitch) + " " + str(curr_start) + " " + str(curr_end)
				else:
					continue
			next_line = n[x+1]
			next_match = re.search(r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', next_line)
			if next_match:
				next_start = next_match.group(2)
				next_end = next_match.group(3)
				next_dur = (float(next_end) - float(next_start))
				if(next_dur <= 0.15):
					curr_end = next_end
					merge = 1
					continue
			curr_dur = (float(curr_end) - float(curr_start))
			tick = int(curr_dur/tick_val)
			self.midi_in.append((int((float)(curr_pitch)),tick))
			begin = float(curr_start)*44100
			end = float(curr_end)*44100
			self.audiofile.append(snd[begin:end])
			merge = 0

def main():

	filename = sys.argv[1]
	aubio_out = open(filename, 'r')
	aubionotes = aubio_out.readlines()
	ad = 1
	tick_val = .0023

	## Reads in input wav, converts it to floating points between -1 and 1
	sampFreq, snd = wavfile.read('input.wav')
	snd = snd / (2.**15)
	monomix = []
	thing1 = system([],[],[],[],[],[],[],[],[],0,[])
	numpy.set_printoptions(threshold='nan')

	thing1.parsemidi(aubionotes,snd)
	thing1.makemidi()
	thing1.makemarkov()
	#print(thing1.first_pitches)
	#thing1.generatemarkov()

















if __name__ == "__main__":
    main()
