import FWCore.ParameterSet.Config as cms

from python.filelist import fileList

process = cms.Process("Demo")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 1000

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    #fileNames = cms.untracked.vstring(
    #    '/store/user/amarini/GenevaMC/HepMC10k_GEN.root'
    #)
    fileNames = cms.untracked.vstring( fileList ),
    duplicateCheckMode = cms.untracked.string("noDuplicateCheck")
)

process.TFileService = cms.Service("TFileService",
		        closeFileFast = cms.untracked.bool(False),
		        fileName = cms.string("Ntuples.root"),
		        )


process.demo = cms.EDAnalyzer('GenAnalysis'
)


process.p = cms.Path(process.demo)
