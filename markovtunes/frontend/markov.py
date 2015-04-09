#!/usr/bin/python

import numpy
from scipy.io import wavfile
import sys
import math
import midi
import wave, struct
import re
from random import randint
import os

tick_val = .0023

class system:

	def __init__(self, audiofile, tracker, midi_in, pitch_list, duration_list, time_list, audiotime_list, p_model, d_model, first_pitches, first_d, gen_result):
		self.audiofile = audiofile
		self.tracker = tracker
		self.midi_in = midi_in
		self.pitch_list = pitch_list
		self.duration_list = duration_list
		self.time_list = time_list
		self.audiotime_list = audiotime_list
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

		#midi.write_midifile("bday.mid", pattern)

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

	def generatemelody(self):

		# num_notes is number of note/duration pairs generated
		# gets sum of chosen row in the model, generates random number in range of sum, then iterates through indexes until
		# it finds the next note.
		#to enforce pitch shifts, add 48 for each
		num_notes = 100
		lastpair = (self.first_pitches[0]*12) + self.first_pitches[1]
		notelust = []
		lagger = self.first_pitches[1]
		chosen = 0
		timelist = []
		notelust.append(self.first_pitches[0]+48)
		notelust.append(self.first_pitches[1]+48)


		for x in range(0,num_notes - 2):


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



				notelust.append(chosen+48)
				lastpair = (lagger*12) + chosen
				lagger = chosen


		self.pitch_list = notelust
		lastdur = self.first_d/110
		durlust = []
		durlust.append(lastdur*110)


		for x in range(0,num_notes-1):

			dur_rowsum = self.d_model[lastdur].sum()
			if dur_rowsum != 0:
				random = randint(1, dur_rowsum)
				dur_runningsum = random
				for num in range(0,15):
					dur_runningsum = dur_runningsum - self.d_model[lastdur][num]
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
				timelist.append((0, lastdur*110*tick_val))
			else:
				timelist.append((timelist[x-1][1], lastdur*110*tick_val+timelist[x-1][1]))


		self.duration_list = durlust
		self.time_list = timelist
		self.gen_result = zip(notelust, durlust)

		#self.updatemodels(sub)

		return self.slice()


		#print(self.p_model)

## this one not needed for Audio
	def updatemodels(self, pairlists):
		# changes the good ones
		start_index = 0
		end_index = 0
		for h in range (0, len(pairlists)):
			start_time = pairlists[h][1]
			end_time = pairlists[h][2]
			flag = 0
			for j in range (0, len(self.time_list)):
				if self.time_list[j][1] > start_time and flag == 0:
					start_index = j-1
					flag = 1
				if self.time_list[j][1] > end_time:
					end_index = j-1
			twoback = self.pitch_list[start_index]%12
			oneback = self.pitch_list[start_index+1]%12

			for x in range(start_index+2, end_index):

				a = self.pitch_list[x]%12
				if pairlists[h][0] == 1:
					self.p_model[(twoback*12)+oneback][a] += 1
				else:
					self.p_model[(twoback*12)+oneback][a] -= 1
				twoback = oneback
				oneback = a

	def slice(self):

		newclip = []
		rate = 44100
		self.audiotime_list[:] = []
		last_point = 0.0
		for i in range(0, len(self.pitch_list)):
			total = len(self.tracker[self.pitch_list[i]%12])
			if total > 0:
				rand = randint(0, total-1)
			else:
				n = [(.00003, .00004)]
				self.audiotime_list.append((last_point, last_point + 1.0/44100.0))
				b = numpy.concatenate([m, n])
				m = b
				continue

			if i == 0:

				m = self.audiofile[self.tracker[self.pitch_list[i]%12][rand]]
				point = (float(len(m))/44100.0)
				self.audiotime_list.append((0.0, point))
				last_point = point
				continue

			n = self.audiofile[self.tracker[self.pitch_list[i]%12][rand]]
			point = (float)(len(m))/44100.0
			self.audiotime_list.append((last_point, last_point + point))
			last_point = last_point + point
			b = numpy.concatenate([m, n ])
			m = b

		#b = [numpy.float32(elem) for elem in b]
		newclip = numpy.array(b)
		wavfile.write('chopped.wav', 44100, newclip)

	def parsemidi(self, aubionotes,snd):
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

	def parsemidi2(self, aubionotes,snd):
		# reads through aubionotes txt file and extracts pitch and duration information.
		# merges notes shorter than 150ms with previous note
		# Populates midi_in & audiofile. format: pitch, start time, end time
		n = aubionotes

		merge = 0
		for x in range(4,len(n)-3):

			curr_line = n[x]
			curr_match = re.search(r'(\d+\.\d+)\s+(\d+\.\d+)\s+(\d+\.\d+)', curr_line)
			if curr_match:
				curr_pitch = curr_match.group(1)
				curr_start = curr_match.group(2)
				curr_end = curr_match.group(3)
				curr_dur = (float(curr_end) - float(curr_start))
				if (curr_dur <= 0.15):
					if (merge == 0):
						last_start = curr_start
						last_pitch = curr_pitch
						merge = 1
						continue
				else:
					if (merge == 1):
						curr_start = last_start
					tick = int(curr_dur/tick_val)
					self.midi_in.append((int((float)(curr_pitch)),tick))
					begin = float(curr_start)*44100
					end = float(curr_end)*44100
					self.audiofile.append(snd[begin:end])
					#wavfile.write('sound'+str(x)+'.wav', 44100, snd[begin:end])	#testing
					merge = 0

	def audio_update(self, pairlists): #List of pairs
		# changes the good ones
		start_index = 0
		end_index = 0
		for h in range (0, len(pairlists)):
			start_time = pairlists[h][0]
			end_time = pairlists[h][1]
			flag = 0
			for j in range (0, len(self.audiotime_list)):
				if self.audiotime_list[j][1] > start_time and flag == 0:
					start_index = j-1
					flag = 1
				if self.audiotime_list[j][1] > end_time:
					end_index = j-1
			twoback = self.pitch_list[start_index]%12
			oneback = self.pitch_list[start_index+1]%12

			for x in range(start_index+2, end_index):

				# if (x == (end_index-1)) and (h==(len(pairlists)-1)):
				# 	import pdb; pdb.set_trace()

				a = self.pitch_list[x]%12
				self.p_model[(twoback*12)+oneback][a] += 1

				twoback = oneback
				oneback = a

def main():

	os.system("aubionotes -v blarg.wav &> blarg.txt")

	filename = "blarg.txt"
	with open(filename, 'r') as aubio_out:
		aubionotes = aubio_out.readlines()
	aubio_out.close()
	## Reads in input wav, converts it to floating points between -1 and 1
	sampFreq, snd = wavfile.read('blarg.wav')
	thing1 = system([],[],[],[],[],[],[],[],[],[],0,[])
	#numpy.set_printoptions(threshold='nan')


	thing1.parsemidi2(aubionotes,snd)
	thing1.makemidi()
	thing1.makemarkov()

	return thing1

	#return thing1.generatemelody()
