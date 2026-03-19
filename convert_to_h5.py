#!/usr/bin/env python3

import sys
import getopt
import h5py
import ROOT
import numpy as np
import os
import math
ROOT.gSystem.Load(f"{os.environ['WCSIM_BUILD_DIR']}/lib/libWCSimRoot.so")

def usage():
    '''Demo script to convert wcsim.root to h5
    '''
    print ("Demo script to convert wcsim.root to h5")
    print ("Usage:")
    print ("convert_to_h5.py [-h] [-f <file_to_convert>] [-o <output_filename>]")
    print ("")
    print ("Options:")
    print ("-h, --help: prints help message")
    print ("-f, --file=<file_to_convert>")
    print ("-o, --out=<output_filename>")
    print ("")

def convert_to_h5():

    fname = None
    fout = 'out.h5'

    try:
        opts, args = getopt.getopt(sys.argv[1:], "hf:o:",
                                   ["help", "file=", "out="])
    except getopt.GetoptError as err:
        print (str(err))
        usage()
        sys.exit(2)

    for opt, val in opts:
        if (opt in ("-h", "--help")):
            usage()
            sys.exit()
        if (opt in ("-f", "--file")):
            fname = val.strip()
        if (opt in ("-o", "--out")):
            fout = val.strip()

    if fname == None:
        print("Missing input file!!")
        usage()
        sys.exit(2)

    chain = ROOT.TChain("wcsimT")
    chain.Add(fname)

    single_file_name = chain.GetFile().GetName()
    f = ROOT.TFile.Open(single_file_name)
    if not f or not f.IsOpen():
        print(f"Error, could not open input file: {single_file_name}")
        return -1
    geotree = f.Get("wcsimGeoT")
    print(f"Geotree has {geotree.GetEntries()} entries")
    if geotree.GetEntries() == 0:
        exit(9)
    geotree.GetEntry(0)
    geo = geotree.wcsimrootgeom
    npmts = geo.GetWCNumPMT()
    print(f"geo has {npmts} PMTs")
    nPMTs_type0 = geo.GetWCNumPMT()
    pmt_posT = []
    pmt_tof = []
    pmt_CylLoc = []
    mPMTNo = []
    mPMT_PMTNo = []

    vg = 2.20027795333758801e8 * 100 / 1.e9 # rough speed of light in water in cm/ns
    max_r = 0
    max_z = 0
    for i in range(nPMTs_type0):
        pmt = geo.GetPMT(i)
        pos = [pmt.GetPosition(j) for j in range(3)]
        dir = [pmt.GetOrientation(j) for j in range(3)]
        mPMTNo.append(pmt.GetmPMTNo())
        mPMT_PMTNo.append(pmt.GetmPMT_PMTNo())
        pmt_CylLoc.append(pmt.GetCylLoc())
        pmtpos = ROOT.TVector3(pos[0], pos[1], pos[2])
        pmt_posT.append(pmtpos)
        #pmt_tof.append((pmtpos - vtx).Mag() / vg)

        #  y-axis is vertical
        if abs(pos[1]) > max_z:
            max_z = abs(pos[1])
        if math.sqrt(pos[0]**2 + pos[2]**2) > max_r and abs(pmt.GetOrientation(1)) > 0.5:
            max_r = math.sqrt(pos[0]**2 + pos[2]**2)

    nevents = chain.GetEntries()
    print("number of entries in the tree: " + str(nevents))
    chain.GetEvent(0)
    event = chain.wcsimrootevent

    vertex = np.zeros((nevents,3),dtype=np.float32)
    direction = np.zeros((nevents,3),dtype=np.float32)
    momentum = np.zeros(nevents,dtype=np.float32)
    pmtQ = np.zeros((nevents,npmts),dtype=np.float32)
    pmtT = np.zeros((nevents,npmts),dtype=np.float32)

    for i in range(nevents):
        event.ReInitialize()
        chain.GetEntry(i)
        trigger = event.GetTrigger(0)

        tracks = trigger.GetTracks()
        primary_track = [t for t in tracks if (t.GetId() == 1)]
        pos3 = np.array([primary_track[0].GetStart(0)*10, -primary_track[0].GetStart(2)*10, primary_track[0].GetStart(1)*10], dtype=np.float32) # in mm
        vertex[i] = pos3
        dir3 = np.array([primary_track[0].GetDir(0), -primary_track[0].GetDir(2), primary_track[0].GetDir(1)], dtype=np.float32)
        direction[i] = dir3
        momentum[i] = primary_track[0].GetP()
        for hit in trigger.GetCherenkovDigiHits():
            if hit.GetT()<100:
                pmt_id = hit.GetTubeId() - 1
                q = hit.GetQ()
                pmtQ[i][pmt_id] = pmtQ[i][pmt_id]+q
                pmtT[i][pmt_id] = np.mean(pmtQ[i][pmt_id]+hit.GetT())

    print('vertex.shape = ',vertex.shape)
    print('direction.shape = ',direction.shape)
    print('momentum.shape = ',momentum.shape)
    print('pmtQ.shape = ',pmtQ.shape)

    with h5py.File(fout,mode='w') as h5fw:
        h5fw.create_dataset('vertex', data=vertex)
        h5fw.create_dataset('direction', data=direction)
        h5fw.create_dataset('momentum', data=momentum)
        h5fw.create_dataset('pmtQ', data=pmtQ)
        h5fw.create_dataset('PMT_pos', data=pmt_posT)
        h5fw.create_dataset('mPMT_slot', data=mPMTNo)
        h5fw.create_dataset('PMT_slot_id', data=mPMT_PMTNo)
        h5fw.create_dataset('pmtT', data=pmtT)
        

if __name__ == '__main__':
    convert_to_h5()