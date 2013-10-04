#!/usr/bin/env python
# vim: ts=2 sw=2 expandtab

import sys
import os

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-i","--infile")
parser.add_option("-o","--outfile")
parser.add_option("-d","--datfile")
(options,args) = parser.parse_args()

import ROOT as r
r.TH1.SetDefaultSumw2()

infile = r.TFile(options.infile)
outfile = r.TFile(options.outfile,"RECREATE")
datfile = open(options.datfile)
datlines = datfile.readlines()

trees={}
hists={}

# function to fill histograms:
def fillHists(trees,hists,histConfig):
  
  for treeName in trees.keys(): # this loops types e.g data, bkg etc.
    histArr=[]
    for hcfg in histConfig: # this loops each histogram type
      histOpts = hcfg[0].split(',')
      assert(len(histOpts)==5 or len(histOpts)==8) # only 1D and 2D distributions supported
      if len(histOpts)==5:
        hist = r.TH1F('%s_%s'%(treeName,histOpts[0]),histOpts[1],int(histOpts[2]),float(histOpts[3]),float(histOpts[4]))
      if len(histOpts)==8:
        hist = r.TH2F('%s_%s'%(treeName,histOpts[0]),histOpts[1],int(histOpts[2]),float(histOpts[3]),float(histOpts[4]),int(histOpts[5]),float(histOpts[6]),float(histOpts[7]))
      histArr.append(hist)
    if treeName in hists.keys():
      print 'WARNING -- overwriting this key %s'%treeName
    hists[treeName] = histArr
  
  for treeName, arrTrees in trees.items(): # this loops types e.g data, bkg etc.
    for tree in arrTrees: # this loops the trees in type e.g diphojet, gjet, qcd
      print treeName, ':', tree.GetName(), ':'
      for ev in range(tree.GetEntries()):
        if ev%10000==0: print '\t', ev, '/', tree.GetEntries()
        tree.GetEntry(ev)
        for i,hcfg in enumerate(histConfig): # this loops each histogram type
          varCfg = hcfg[1]
          if len(varCfg.split(';'))==1: # 1D hist
            if 'form:' in varCfg:
              var=varCfg.split('form:')[1]
              var=var.replace('tv:','tree.')
              execLine = 'hists[treeName][i].Fill(%s,tree.evweight)'%var
              exec execLine
            else: 
              var=varCfg
              hists[treeName][i].Fill(getattr(tree,var),tree.evweight)
          
          elif len(varCfg.split(';'))==2: # 2D hist
            var1 = varCfg.split(';')[0]
            var2 = varCfg.split(';')[1]
            if 'form:' in var1:
              var1=var1.split('form:')[1]
              var1=var1.replace('tv:','tree.')
            else:
              var1 = 'tree.%s'%var1
            if 'form:' in var2:
              var2=var2.split('form:')[1]
              var2=var2.replace('tv:','tree.')
            else:
              var2 = 'tree.%s'%var2
            execLine = 'hists[treeName][i].Fill(%s,%s,tree.evweight)'%(var1,var2)
            exec execLine
              
          else:
            sys.exit('ERROR - only 1D and 2D histograms supported')

def writeHists(hists,outfile):
  outfile.cd()
  for name,histArr in hists.items():
    for hist in histArr:
      hist.Write()

# set up tree dict
for line in datlines:
  if line.startswith('#') or line=='\n':
    continue
  if line.startswith('treeDir'): 
    treeDir=line.split('=')[1].strip('\n')
  if 'Trees' in line:
    name=line.split('Trees')[0]
    types=line.split('=')[1].strip('\n')
    if name=='alt':
      name=line.split('=')[1].split(':')[0]
      types=line.split('=')[1].split(':')[1].strip('\n')
    treeArr=[]
    for t in types.split(','):
      tree = infile.Get('%s/%s'%(treeDir,t))
      if not tree: print 'WARNING -- this tree %s/%s is null'%(tree,t)
      treeArr.append(tree)
    if name in trees.keys():
      print 'WARNING -- this key %s is being overwritten'%name
    trees[name] = treeArr

# set hist dict
histConfig=[]
for line in datlines:
  if line.startswith('#') or line=='\n':
    continue
  if line.startswith('hist'):
    opts = line.split()
    cfg=[]
    for opt in opts:
      if opt.startswith('hist'):
        cfg.append(opt.split('=')[1].strip('\n'))
      if opt.startswith('var'):
        cfg.append(opt.split('=')[1].strip('\n'))
      if opt.startswith('cut'):
        cfg.append(opt.split('=')[1].strip('\n'))
    histConfig.append(cfg)

print trees
print '\n'
print histConfig

fillHists(trees,hists,histConfig)
writeHists(hists,outfile)

outfile.Close()
infile.Close()
  

