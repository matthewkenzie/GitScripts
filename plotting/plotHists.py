#!/usr/bin/env python
# vim: ts=2 sw=2 expandtab

import os,sys
from optparse import OptionParser
from optparse import OptionGroup

parser = OptionParser()
parser.add_option("-i","--infile")
parser.add_option("-d","--datfile")
parser.add_option("-w","--wait",default=False,action="store_true")
parser.add_option("-v","--verbose",default=False,action="store_true")
groupPlot = OptionGroup(parser,"Per plot options")
groupPlot.add_option("--outDir",default='',help="outfile path")
groupPlot.add_option("--canv",default=[-1,-1])
groupPlot.add_option("--varName",type="str",default=',',help="variable name")
groupPlot.add_option("--xtitle",type="str",default='')
groupPlot.add_option("--ytitle",type="str",default='')
groupPlot.add_option("--xrangeuser",default=[-1.,-.1])
groupPlot.add_option("--yrangeuser",default=[-1.,-1.])
groupPlot.add_option("--logx",default=False,action="store_true")
groupPlot.add_option("--logy",default=False,action="store_true")
groupPlot.add_option("--drawEfficiency",default=False,action="store_true")
groupPlot.add_option("--drawResid",default=False,action="store_true")
groupPlot.add_option("--drawROC",default=False,action="store_true")
groupPlot.add_option("--grid",default=False,action="store_true")
groupPlot.add_option("--leg",default=[])
groupPlot.add_option("--plotName",type="str",default='',help="outfile name")
parser.add_option_group(groupPlot)
groupHist = OptionGroup(parser,"Per histogram options")
groupHist.add_option("--type",type='str',default='',help="eg sig/bkg/data")
groupHist.add_option("--scale",type="float",default=-1.)
groupHist.add_option("--norm",type="float",default=-1.)
groupHist.add_option("--color",type="int",default=-1)
groupHist.add_option("--width",type="int",default=-1)
groupHist.add_option("--style",type="int",default=-1)
groupHist.add_option("--marker",type="int",default=-1)
groupHist.add_option("--rebin",type="int",default=-1)
groupHist.add_option("--legStr",type="str",default='')
groupHist.add_option("--draw",type="str",default='')
parser.add_option_group(groupHist)
(opts,args) = parser.parse_args()

opts.atStart=False
opts.atEnd=False
opts.rocBHist=''
opts.residHist=''
opts.resTyp=''
opts.resOpt=''
hists=[]

import ROOT as r
r.TH1.SetDefaultSumw2()
r.gStyle.SetOptStat(0)
if not opts.wait: r.gROOT.SetBatch()

infile = r.TFile(opts.infile)
datfile = open(opts.datfile)
datlines = datfile.readlines()

def printOptions():
  for optName in [x.dest for x in parser._get_all_options()[1:]]:
    print '%10s :'%optName, getattr(opts,optName)

def setAttributes(hist):
    
  for optName in [x.dest for x in parser._get_all_options()[1:]]:
    if str(getattr(opts,optName))=='-1' or str(getattr(opts,optName))=='-1.0' or str(getattr(opts,optName))=='': 
      continue
    else: 
      if optName=='rebin': hist.Rebin(opts.rebin)
      if optName=='norm': hist.Scale(opts.norm/hist.Integral())
      if optName=='scale': hist.Scale(opts.scale)
      if optName=='legStr': leg.AddEntry(hist,opts.legStr.replace('\\',' ').replace('EQ','='),opts.draw.replace('hist','l'))
      
      if optName=='draw':
        if opts.draw=='lep':
          hist.SetMarkerStyle(opts.marker)
          hist.SetMarkerColor(opts.color)
          hist.SetLineColor(opts.color)
          hist.SetLineWidth(opts.width)
          hist.SetLineStyle(opts.style)
        elif opts.draw=='f' or opts.draw=='fhist':
          hist.SetFillColor(opts.color)
          hist.SetLineColor(opts.color)
          hist.SetLineWidth(opts.width)
          hist.SetFillStyle(opts.style)
        elif opts.draw=='l' or opts.draw=='hist':
          hist.SetLineColor(opts.color)
          hist.SetFillStyle(0)
          hist.SetLineWidth(opts.width)
          hist.SetLineStyle(opts.style)
        else:
          print 'WARNING -- unrecognised draw option for %s -- %s'%(hist.GetName(),opts.draw)
          continue

def getEfficiency(hist):
  if opts.verbose: print 'Calculating efficiency for %s'%hist.GetName()
  effHist = hist.Clone('%s_eff'%hist.GetName())
  for b in range(1,hist.GetNbinsX()+1):
    effHist.SetBinContent(b,hist.Integral(0,b)/hist.Integral())
  return effHist

def getROC(shist,bhist):
  if opts.verbose: print 'Calculating ROC curve for %s against %s'%(shist.GetName(),bhist.GetName())
  assert(shist.GetNbinsX()==bhist.GetNbinsX())
  assert(shist.GetBinLowEdge(1)==bhist.GetBinLowEdge(1))
  assert(shist.GetBinLowEdge(shist.GetNbinsX()+1)==bhist.GetBinLowEdge(bhist.GetNbinsX()+1))
  
  gr = r.TGraph()
  p=0
  for b in range(1,shist.GetNbinsX()+1):
    gr.SetPoint(p,bhist.Integral(0,b)/bhist.Integral(),shist.Integral(0,b)/shist.Integral())
    p+=1
  gr.SetLineColor(shist.GetLineColor())
  gr.SetLineWidth(shist.GetLineWidth())
  gr.GetXaxis().SetTitle(shist.GetXaxis().GetTitle())
  gr.GetYaxis().SetTitle(shist.GetYaxis().GetTitle())
  return gr

def getResid(hist,rhist):
  if opts.verbose: print 'Calculating residual for %s over %s'%(hist.GetName(),rhist.GetName())
  assert(hist.GetNbinsX()==rhist.GetNbinsX())
  assert(hist.GetBinLowEdge(1)==rhist.GetBinLowEdge(1))
  assert(hist.GetBinLowEdge(hist.GetNbinsX()+1)==rhist.GetBinLowEdge(rhist.GetNbinsX()+1))

  resid = hist.Clone('%s_res'%hist.GetName())

  if opts.resTyp=='diff':
    resid.Add(rhist,-1.)
    resid.GetYaxis().SetTitle('Residual difference')
  elif opts.resTyp=='frac':
    resid.Divide(rhist)
    resid.GetYaxis().SetTitle('Residual ratio')
  else:
    sys.exit('drawResid option %s not recognised\n'%opts.resTyp)
  return resid

def applyMyOpts(hist):
    hist[0].GetXaxis().SetLabelSize(0.045)
    hist[0].GetYaxis().SetLabelSize(0.045)
    hist[0].GetXaxis().SetTitleSize(0.045)
    hist[0].GetYaxis().SetTitleSize(0.045)
    hist[0].GetXaxis().SetTitleOffset(1.)
    hist[0].GetYaxis().SetTitleOffset(1.1)

def drawHists(hists,leg,name):

  os.system('mkdir -p %s'%opts.outDir)
  canvas = r.TCanvas()
  if opts.canv[0]>0 and opts.canv[1]>0:
    #canvas = r.TCanvas("canvas","",opts.canv[0],opts.canv[1])
    canvas.SetWindowSize(opts.canv[0],opts.canv[1])
    canvas.SetCanvasSize(opts.canv[0],opts.canv[1])
    canvas.SetLeftMargin(0.15)

  if opts.resOpt=='same':
    padUp = r.TPad("upper","",0.,0.33,1.0,1.0)
    padDn = r.TPad("down","",0.,0.,1.0,0.33)
    padUp.SetLeftMargin(0.15)
    padDn.SetLeftMargin(0.15)
    padDn.SetBottomMargin(0.2)
    padUp.SetTickx()
    padDn.SetTickx()
    padUp.SetTicky()
    padDn.SetTicky()

  residHists=[]
  for hist in hists:
    applyMyOpts(hist)
    if hist[1]=='f' or hist[1]=='l': hist[1]+='hist'
    if opts.drawEfficiency: hist[0] = getEfficiency(hist[0])
    if opts.drawROC: 
      hist[0] = getROC(hist[0],opts.rocBHist)
    if opts.drawResid: 
       if hist[0]!=opts.residHist:
         residHists.append([getResid(hist[0],opts.residHist),hist[1]])
  
    if opts.xrangeuser[0]>0. and opts.xrangeuser[1]>0.:
      hist[0].GetXaxis().SetRangeUser(opts.xrangeuser[0],opts.xrangeuser[1])
    if opts.yrangeuser[0]>0. and opts.yrangeuser[1]>0.:
      hist[0].GetYaxis().SetRangeUser(opts.yrangeuser[0],opts.yrangeuser[1])
   
  if opts.resOpt=='same':
    padUp.cd()
  else:
    canvas.cd()
  
  if opts.drawEfficiency:
    hists[0][0].Draw("LHIST")
    for hist in hists[1:]:
      hist[0].Draw('LHISTsame')
  elif opts.drawROC:
    hists[0][0].Draw("AL")
    for hist in hists[1:]:
      hist[0].Draw("Lsame")
  else:
    hists[0][0].Draw(hists[0][1])
    for hist in hists[1:]:
      hist[0].Draw('%ssame'%hist[1])

  leg.Draw()
  canvas.SetTickx()
  canvas.SetTicky()
  if opts.grid: 
    canvas.SetGrid()
  if opts.logx:
    canvas.SetLogx()
  if opts.logy:
    canvas.SetLogy()
  canvas.RedrawAxis()
  canvas.RedrawAxis("g")
  canvas.Update()
  canvas.Modified()
  if not opts.resOpt=='same':
    if opts.wait: 
      forms = raw_input('File format? (comma seperated - pdf default)\n')
      if forms=='q' or forms=='quit': sys.exit()
      for form in forms:
        canvas.Print('%s/%s.%s'%(opts.outDir,name,form))
    canvas.Print('%s/%s.pdf'%(opts.outDir,name))
   
  if opts.drawResid:
    if opts.resOpt=='same':
      padDn.cd()
      residHists[0][0].GetYaxis().SetTitleSize(0.09)
      residHists[0][0].GetXaxis().SetTitleSize(0.09)
      residHists[0][0].GetYaxis().SetLabelSize(0.09)
      residHists[0][0].GetXaxis().SetLabelSize(0.09)
      residHists[0][0].GetYaxis().SetTitleOffset(0.75)
      residHists[0][0].GetXaxis().SetTitleOffset(0.85)
      residHists[0][0].GetYaxis().SetNdivisions(505)
    else:
      canvas.cd()
    residHists[0][0].Draw("AXIS")
    l = r.TLine()
    l.SetLineWidth(3)
    l.SetLineColor(2)
    l.SetLineStyle(r.kDashed)
    yval=0.
    if opts.resTyp=='diff': yval=0.
    elif opts.resTyp=='frac': yval=1.
    else: sys.exit('drawResid type %s not recognised'%opts.resTyp)
    
    if opts.xrangeuser[0]>0 and opts.xrangeuser[1]>1:
      l.DrawLine(opts.xrangeuser[0],yval,opts.xrangeuser[2],yval)
    else:
      l.DrawLine(residHists[0][0].GetBinLowEdge(1),yval,residHists[0][0].GetBinLowEdge(residHists[0][0].GetNbinsX()+1),yval)
    for hist in residHists:
      hist[0].Draw('%ssame'%hist[1])
    #if opts.resOpt!='same': leg.Draw()
    canvas.SetTickx()
    canvas.SetTicky()
    if opts.grid: 
      canvas.SetGrid()
    if opts.logx:
      canvas.SetLogx()
    if opts.logy:
      canvas.SetLogy()
    canvas.RedrawAxis()
    canvas.RedrawAxis("g")
    canvas.Update()
    canvas.Modified()
    if opts.resOpt=='same':
      canvas.cd()
      padUp.Draw()
      padDn.Draw()
      padUp.RedrawAxis()
      padDn.RedrawAxis()
      if opts.grid:
        padUp.SetGrid()
        padDn.SetGrid()
      if opts.logx:
        padUp.SetLogx()
        padDn.SetLogx()
      if opts.logy:
        padUp.SetLogy()
      padUp.SetFillStyle(4000)
      padDn.SetFillStyle(4000)
      padUp.RedrawAxis("g")
      padDn.RedrawAxis("g")
      padUp.Update()
      padUp.Modified()
      padDn.Update()
      padDn.Update()
      canvas.cd()
      canvas.Update()
      canvas.Modified()

    if opts.wait:
      forms = raw_input('File format? (pdf default)\n')
      if forms=='q' or forms=='quit': sys.exit()
      for form in forms:
        canvas.Print('%s/%s_res.%s'%(opts.outDir,name,form))
    canvas.Print('%s/%s_res.pdf'%(opts.outDir,name))

## start main
inComment=False

for line in datlines:
  # skip comments and new lines
  if line.startswith('->'):
    inComment = not inComment
    continue
  if inComment: 
    continue
  if line.startswith('#') or line=='\n': 
    continue
  line = line.strip('\n')
  
  # some special cases
  if line.startswith('varName'):
    opts.varName = line.split('=')[1]
    opts.drawEfficiency=False
    opts.drawROC=False
    opts.drawResid=False
    opts.grid=False
    opts.logx=False
    opts.logy=False
    opts.atStart=True
    hists=[]
  else:
    opts.atStart=False
  if line.startswith('plotName'):
    opts.plotName = line.split('=')[1]
    opts.atEnd=True
    drawHists(hists,leg,opts.plotName)
  else:
    opts.atEnd=False
  
  # legend
  if line.startswith('leg'):
    leg=line.split('=')[1].split(',')
    assert(len(leg)==4)
    leg = r.TLegend(float(leg[0]),float(leg[1]),float(leg[2]),float(leg[3]))
    leg.SetFillColor(0)
    leg.SetLineColor(0)

  # ROC curves
  if line.startswith('drawROC'):
    opts.rocBHist=line.split('=')[1]
    if opts.rocBHist!='':
      opts.drawROC=True
      opts.rocBHist = infile.Get('%s_%s'%(opts.rocBHist,opts.varName))
  
  # residuals
  elif line.startswith('drawResid'):
    opts.residHist=line.split('=')[1]
    if opts.residHist!='':
      opts.drawResid=True
      hname=opts.residHist.split(':')[0]
      opts.resTyp=opts.residHist.split(':')[1]
      opts.resOpt=opts.residHist.split(':')[2]
      opts.residHist = infile.Get('%s_%s'%(hname,opts.varName))
  
  # get and set up the hists 
  elif line.startswith('type'):
    hCfg={}
    for opt in line.split():
      hCfg[opt.split('=')[0]] = opt.split('=')[1]

    hist = infile.Get('%s_%s'%(hCfg['type'],opts.varName))
    hist.GetXaxis().SetTitle(opts.xtitle)
    hist.GetYaxis().SetTitle(opts.ytitle)

    for opt,val in hCfg.items():
      if type(getattr(opts,opt))!=type('str'):
        val = eval(val,{},{})
      setattr(opts,opt,val)

    if opts.verbose: printOptions()
    # set hist attributes here:
    setAttributes(hist)
    
    hists.append([hist,hCfg['draw']])
  
  # passing other options here
  else:
    optName = line.split('=')[0]
    optVal = line.split('=')[1]
    if optName not in [x.dest for x in parser._get_all_options()[1:]]:
      print 'Unrecognised option: %s'%optName
      sys.exit()
    else:
      if ',' in optVal: 
        els = optVal.split(',')
        convEls=[]
        for el in els:
          el = eval(el,{},{})
          convEls.append(el)
        setattr(opts,optName,convEls)
      else:
        if type(getattr(opts,optName))==type(optVal):
          setattr(opts,optName,optVal)
        else:
          #print type(getattr(opts,optName))
          #print optVal
          val = map(type(getattr(opts,optName)),optVal)
          setattr(opts,optName,val) # casts string to approp data type

  """
  if line.startswith('outDir'):
    opts.outDir=line.split('=')[1]
    os.system('mkdir -p %s'%opts.outDir)

  if line.startswith('canv'):
    opts.canv = [int(line.split('=')[1].split(',')[0]),int(line.split('=')[1].split(',')[1])]

  if line.startswith('varName'):
    opts.varName=line.split('=')[1]
    opts.drawEfficiency=False
    opts.drawROC=False
    opts.drawResid=False
    opts.grid=False
    opts.atStart=True
    hists=[]
  else:
    opts.atStart=False

  if line.startswith('xtitle'):
    opts.xtitle=line.split('=')[1]

  if line.startswith('ytitle'):
    opts.ytitle=line.split('=')[1]

  if line.startswith('xrangeuser'):
    opts.xrangeuser=[float(line.split('=')[1].split(',')[0]),float(line.split('=')[1].split(',')[1])]

  if line.startswith('yrangeuser'):
    opts.yrangeuser=[float(line.split('=')[1].split(',')[0]),float(line.split('=')[1].split(',')[1])]

  if line.startswith('drawEfficiency'):
    opts.drawEfficiency=int(line.split('=')[1])

  if line.startswith('drawROC'):
    opts.rocBHist=line.split('=')[1]
    if opts.rocBHist!='':
      opts.drawROC=True
      opts.rocBHist = infile.Get('%s_%s'%(opts.rocBHist,opts.varName))

  if line.startswith('drawResid'):
    opts.residHist=line.split('=')[1]
    if opts.residHist!='':
      opts.drawResid=True
      hname=opts.residHist.split(':')[0]
      opts.resTyp=opts.residHist.split(':')[1]
      opts.resOpt=opts.residHist.split(':')[2]
      opts.residHist = infile.Get('%s_%s'%(hname,opts.varName))

  if line.startswith('grid'):
    opts.grid = int(line.split('=')[1])

  if line.startswith('logx'):
    opts.logx = int(line.split('=')[1])

  if line.startswith('logy'):
    opts.logy = int(line.split('=')[1])

  if line.startswith('leg'):
    legStr=line.split('=')[1].split(',')
    assert(len(legStr)==4)
    leg = r.TLegend(float(legStr[0]),float(legStr[1]),float(legStr[2]),float(legStr[3]))
    leg.SetFillColor(0)
    leg.SetLineColor(0)

  if line.startswith('type'):
    hCfg={}
    for opt in line.split():
      hCfg[opt.split('=')[0]] = opt.split('=')[1]

    hist = infile.Get('%s_%s'%(hCfg['type'],opts.varName))
    hist.GetXaxis().SetTitle(opts.xtitle)
    hist.GetYaxis().SetTitle(opts.ytitle)
    
    if 'rebin' in hCfg.keys():
      hist.Rebin(int(hCfg['rebin']))
    
    if 'draw' not in hCfg.keys():
      print 'WARNING -- no draw option for %s'%hist.GetName()
      continue
    
    if 'norm' in hCfg.keys():
      hist.Scale(float(hCfg['norm'])/hist.Integral())
    if 'scale' in hCfg.keys():
      hist.Scale(float(hCfg['scale']))
    if 'leg' in hCfg.keys():
      leg.AddEntry(hist,hCfg['leg'].replace('\\',' ').replace('EQ','='),hCfg['draw'].replace('hist','l'))
      if opts.verbose: print 'adding key:', hist.GetName()

    if hCfg['draw']=='lep':
      if 'marker' in hCfg.keys(): 
        hist.SetMarkerStyle(int(hCfg['marker']))
      if 'color' in hCfg.keys():
        hist.SetMarkerColor(int(hCfg['color']))
        hist.SetLineColor(int(hCfg['color']))
      if 'width' in hCfg.keys():
        hist.SetLineWidth(int(hCfg['width']))
      if 'style' in hCfg.keys():
        hist.SetLineStyle(int(hCfg['style']))

    elif hCfg['draw']=='f' or hCfg['draw']=='fhist' or hCfg['draw']=='lf':
      if 'color' in hCfg.keys():
        hist.SetLineColor(int(hCfg['color']))
        hist.SetFillColor(int(hCfg['color']))
      if 'width' in hCfg.keys():
        hist.SetLineWidth(int(hCfg['width']))
      if 'style' in hCfg.keys():
        hist.SetLineStyle(int(hCfg['style']))
    
    elif hCfg['draw']=='l' or hCfg['draw']=='hist':
      if 'color' in hCfg.keys():
        hist.SetLineColor(int(hCfg['color']))
        hist.SetFillStyle(0)
      if 'width' in hCfg.keys():
        hist.SetLineWidth(int(hCfg['width']))
      if 'style' in hCfg.keys():
        hist.SetLineStyle(int(hCfg['style']))

    else:
      print 'WARNING -- unrecognised draw option for %s -- %s'%(hist.GetName(),hCfg['draw'])
      continue

    hists.append([hist,hCfg['draw']])

  if line.startswith('plotName'):
    opts.plotName=line.split('=')[1]
    opts.atEnd=True
    drawHists(hists,leg,opts.plotName)
  else:
    opts.atEnd=False
  """

    
