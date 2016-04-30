import sys,os
import ROOT


f = ROOT.TFile.Open("Ntuples.root")
tree = f.Get("demo/events")


def envelope(histos, idxList = [] ,name="env"):
	target= histos[0].Clone(name)
	target.SetTitle(name)
	target.Reset("ACE")
	for bin in range(0, histos[0].GetNbinsX()+2):
		min = -100 ## xSec >0
		max = -100
		for idx in idxList:
			c = histos[idx].GetBinContent(bin)
			if min<c or min<0: min=c
			if max>c or max<0: max=c
		target.SetBinContent(bin, (max+min)/2.)
		target.SetBinError(bin, (max-min)/2.)
	return target

nentries = tree.GetEntries()

h=ROOT.TH1D("template","template",20,0,100)

histos=[]

for idx in range(0,11):
	histos.append( h.Clone("weight%d"%idx) )

for ientry in range(0,nentries):
	tree.GetEntry(ientry)

	for idx in range(0,11):
		histos[idx].Fill(tree.ptZ,tree.weights[idx])

c=ROOT.TCanvas()
#c.SetLogx()
c.SetLogy()


hard=envelope(histos,[0,1,2],"hard")
resum=envelope(histos,[0] + range(3,9) , "resum")
scale=envelope(histos,[0] + range(9,11) , "scale")

histos[0].Draw("AXIS")
histos[0].SetMarkerColor(ROOT.kBlack)
histos[0].SetLineColor(ROOT.kBlack)
histos[0].SetMarkerStyle(20)

hard.SetFillColor(ROOT.kRed -4 )

resum.SetFillColor(ROOT.kGreen +2 )
resum.SetFillStyle(3004 )

scale.SetFillColor(ROOT.kBlue )
scale.SetFillStyle(3005 )


hard.Draw("E3 SAME")
scale.Draw("E3 SAME")
resum.Draw("E3 SAME")

histos[0].Draw("PE SAME")
histos[0].SetTitle("nominal")

c.BuildLegend()

raw_input("ok?")
c.SaveAs("ptZ.pdf")
c.SaveAs("ptZ.png")
