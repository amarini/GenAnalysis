import sys,os
import ROOT
from array import array
import math

sw=ROOT.TStopwatch()

f = ROOT.TFile.Open("GenevaNtuples.root")
tree = f.Get("demo/events")


ZPtList=[0,1.25,2.5,3.75,5,6.25,7.5,8.75,10,11.25,12.5,15,17.5,20,25,30,35,40,45,50,60,70,80,90,100,110,130,150,170,190,220,250,400,1000]
ZPtBins=array('f',ZPtList)
PhiStarList=[0,0.001,0.002,0.003,0.004,0.005,0.006,0.007,0.008,0.01,0.012,0.014,0.016,0.018,0.021,0.024,0.027,0.030,0.034,0.038,0.044,0.050,0.058,0.066,0.076,0.088,0.10,0.12,0.14,0.16,0.18,0.20,0.24,0.28,0.34,0.42,0.52,0.64,0.8,1.0,1.5,2,3]
PhiStarBins=array('f',PhiStarList)
Lep1PtList=[25,26.3,27.6,28.9,30.4,31.9,33.5,35.2,36.9,38.8,40.7,42.8,44.9,47.1,49.5,52.0,54.6,57.3,60.7,65.6,72.2,80.8,92.1,107,126,150,200,300]
Lep1PtBins=array('f',Lep1PtList)
Lep2PtList=[25,26.3,27.6,28.9,30.4,31.9,33.5,35.2,36.9,38.8,40.7,42.8,44.9,47.1,49.5,52.0,54.6,57.3,60.7,65.6,72.2,80.8,92.1,107,126,150]
Lep2PtBins=array('f',Lep2PtList)
LepNegPtList=[25,26.3,27.6,28.9,30.4,31.9,33.5,35.2,36.9,38.8,40.7,42.8,44.9,47.1,49.5,52.0,54.6,57.3,60.7,65.6,72.2,80.8,92.1,107,126,150,200,300]
LepNegPtBins=array('f',LepNegPtList)
LepPosPtList=[25,26.3,27.6,28.9,30.4,31.9,33.5,35.2,36.9,38.8,40.7,42.8,44.9,47.1,49.5,52.0,54.6,57.3,60.7,65.6,72.2,80.8,92.1,107,126,150,200,300]
LepPosPtBins=array('f',LepPosPtList)

out=ROOT.TFile("Geneva_Histograms.root","RECREATE")
hZPt=ROOT.TH1D("ZPt","ZPt",len(ZPtBins)-1,ZPtBins)
hPhiStar=ROOT.TH1D("PhiStar","PhiStar",len(PhiStarBins)-1,PhiStarBins)
hLep1Pt=ROOT.TH1D("Lep1Pt","Lep1Pt",len(Lep1PtBins)-1,Lep1PtBins)
hLep2Pt=ROOT.TH1D("Lep2Pt","Lep2Pt",len(Lep2PtBins)-1,Lep2PtBins)
hLepNegPt=ROOT.TH1D("LepNegPt","LepNegPt",len(LepNegPtBins)-1,LepNegPtBins)
hLepPosPt=ROOT.TH1D("LepPosPt","LepPosPt",len(LepPosPtBins)-1,LepPosPtBins)
hZRap=ROOT.TH1D("ZRap","ZRap",24,0,2.4)

hList=[ hZPt,hZRap,hPhiStar,hLep1Pt,hLep2Pt,hLepPosPt,hLepNegPt ]
for h in hList:
	h.Sumw2()

def DeltaPhi(phi1,phi2):
	dphi=phi1-phi2
	while dphi > math.pi : dphi -= 2*math.pi
	while dphi < -math.pi : dphi += 2*math.pi
	return abs(dphi)	
muMass=0.1057
## normalization
Sum=0.0
Fiducial=0.0
nentries=tree.GetEntries()
sw.Start()
for ientry in range(0,nentries):
	if ientry % 10000 == 1:
		sw.Stop()
		seconds=(nentries-ientry) *sw.RealTime()/1e4
		time=""
		if seconds > 60: 
			time += "%dm "%(int(seconds)/60)
			seconds -= (int(seconds)/60) *60
		time += "%ds"%int(seconds) 
		print "\rDoing entry %d of %d (%.1fs) \t= %.1f%% \tleft %s                  "%(ientry,nentries,sw.RealTime(),float(ientry)/nentries*100,time),
		sys.stdout.flush()
		sw.Start()
	tree.GetEntry(ientry)
	Sum += tree.weight
	if tree.pt1 < 25 or tree.pt2 <25: continue
	if abs(tree.eta1)>2.4 or abs(tree.eta2)>2.4 : continue
	if tree.mZ < 60 or tree.mZ >120 : continue
	if tree.pdgId1*tree.pdgId2 != -13*13 : 
		print "OPS, this should never happen"
		continue  ## OS SF muon , only muon
	Fiducial += tree.weight
	hZPt.Fill(tree.ptZ, tree.weight)
	
	## PHI STAR
	l1=ROOT.TLorentzVector()
	l2=ROOT.TLorentzVector()
	l1.SetPtEtaPhiM(tree.pt1,tree.eta1,tree.phi1,muMass)
	l2.SetPtEtaPhiM(tree.pt2,tree.eta2,tree.phi2,muMass)
	phiacop=math.pi-DeltaPhi(tree.phi1,tree.phi2);
	#if lq1<0
	if tree.pdgId1 >0: costhetastar=math.tanh((l1.Rapidity()-l2.Rapidity())/2.)
	else: costhetastar=math.tanh((l2.Rapidity()-l1.Rapidity())/2.)
        phistar=math.tan(phiacop/2.)*math.sqrt(1-pow(costhetastar,2))
	hPhiStar.Fill(phistar,tree.weight)
	hZRap.Fill(abs(tree.yZ),tree.weight)
	if tree.pt1>tree.pt2: 
		hLep1Pt.Fill(tree.pt1,tree.weight)
		hLep2Pt.Fill(tree.pt2,tree.weight)
	else: 
		hLep1Pt.Fill(tree.pt2,tree.weight)
		hLep2Pt.Fill(tree.pt1,tree.weight)
	if tree.pdgId1 >0: ## neg
		hLepNegPt.Fill(tree.pt1,tree.weight)
		hLepPosPt.Fill(tree.pt2,tree.weight)
	else: ## 1=pos                          
		hLepNegPt.Fill(tree.pt2,tree.weight)
		hLepPosPt.Fill(tree.pt1,tree.weight)

print 
print "---------------------------------------------------"
print "Sum=",Sum,"nentries=",nentries,"xsec=",Sum/nentries
print "Fiducial xsec=",Fiducial/nentries
print "---------------------------------------------------"

for h in hList: 
	h.Scale(1./float(nentries))
	g=ROOT.TGraphAsymmErrors()
	g.SetName(h.GetName() + "_stat")
	for ibin in range(0,h.GetNbinsX()):
		y=h.GetBinContent(ibin+1)
		e=h.GetBinError(ibin+1)
		x=h.GetBinCenter(ibin+1)
		w=h.GetBinWidth(ibin+1)
		exl=x-h.GetBinLowEdge(ibin+1) 
		exh=h.GetBinLowEdge(ibin+2) -x
		n=g.GetN()
		g.SetPoint(n,x,y/w) ## g is divided for the bin width
		g.SetPointError(n,exl,exh,e/w,e/w)
	g.Write()
	h.Write()

## Save Additional informations
S=ROOT.TNamed("Sum","%e"%Sum)
S.Write()
xsec=ROOT.TNamed("xsec","%e"%(Sum/nentries))
xsec.Write()
Fid=ROOT.TNamed("fiducial","%e"%(Fiducial/nentries))
Fid.Write()
out.Close()
f.Close()
#h.Scale(1./Sum)
