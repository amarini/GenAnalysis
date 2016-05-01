// -*- C++ -*-
//
// Package:    GenAnalysis/GenAnalysis
// Class:      GenAnalysis
// 
/**\class GenAnalysis GenAnalysis.cc GenAnalysis/GenAnalysis/plugins/GenAnalysis.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Andrea Carlo Marini
//         Created:  Mon, 08 Feb 2016 10:11:05 GMT
//
//


// system include files
#include <memory>
#include <map>
#include <string>
using namespace std;

// user include files
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/one/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
using namespace reco;

#include "SimDataFormats/GeneratorProducts/interface/GenEventInfoProduct.h"
#include "SimDataFormats/GeneratorProducts/interface/GenRunInfoProduct.h"

#include "FWCore/ServiceRegistry/interface/Service.h"
#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "CommonTools/Utils/interface/TFileDirectory.h"

//
// class declaration
//
//
#include "TTree.h"
#include "TH1D.h"
#include "TLorentzVector.h"

// If the analyzer does not use TFileService, please remove
// the template argument to the base class so the class inherits
// from  edm::one::EDAnalyzer<> and also remove the line from
// constructor "usesResource("TFileService");"
// This will improve performance in multithreaded jobs.

class GenAnalysis : public edm::one::EDAnalyzer<edm::one::SharedResources>  {
   public:
      explicit GenAnalysis(const edm::ParameterSet&);
      ~GenAnalysis();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:
      virtual void beginJob() override;
      virtual void analyze(const edm::Event&, const edm::EventSetup&) override;
      virtual void endJob() override;

      // ----------member data ---------------------------
      //edm::Handle<GenRunInfoProduct> runinfo_handle; 
      //edm::EDGetTokenT<GenRunInfoProduct> runinfo_token;

      edm::EDGetTokenT<edm::View<reco::GenParticle> > gp_token;
      edm::Handle<edm::View<reco::GenParticle> > gp_handle; 

      edm::Handle<GenEventInfoProduct> info_handle;
      edm::EDGetTokenT<GenEventInfoProduct> info_token;

      // 

      edm::Service<TFileService> fileService_;

      // tree
      TTree *tree_;
	
      map<string, float> container_;

      inline void Branch(string name){ tree_->Branch( name.c_str(), &container_[name],(name+"/F").c_str());}
      inline void ClearContainer(){ for(auto& p : container_ ) p.second=-999.;}

      // --- save all the w
      vector<double> *weights{0};
};

//
// constants, enums and typedefs
//

//
// static data member definitions
//
//
//GenEventInfoProduct            "source"           "generator"   "GEN"
//edm::HepMCProduct              "source"           "generator"   "GEN"
//edm::TriggerResults            "TriggerResults"   ""            "GEN"
//vector<int>                    "genParticles"     ""            "GEN"
//vector<reco::GenParticle>      "genParticles"     ""            "GEN"

//
// constructors and destructor
//
GenAnalysis::GenAnalysis(const edm::ParameterSet& iConfig) :
	gp_token ( consumes<edm::View<reco::GenParticle> >( edm::InputTag("genParticles")) ),
	info_token ( consumes< GenEventInfoProduct >( edm::InputTag("source","generator")) ) // Usually only generetor
	//runinfo_token ( consumes<GenRunInfoProduct,edm::InRun>(iConfig.getParameter<edm::InputTag>("") ) )

{
   //now do what ever initialization is needed
   usesResource("TFileService");
    tree_ = fileService_ -> make<TTree>("events", "events");

    Branch("pt1");
    Branch("pt2");
    Branch("eta1");
    Branch("eta2");
    Branch("phi1");
    Branch("phi2");
    Branch("m1");
    Branch("m2");
    Branch("pdgId1");
    Branch("pdgId2");

    Branch("ptZ");
    Branch("yZ");
    Branch("phiZ");
    Branch("mZ");

    Branch("weight");

    weights= new vector<double>();
    tree_->Branch("weights","vector<double>",&weights);
}


GenAnalysis::~GenAnalysis()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
GenAnalysis::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
   using namespace edm;
   ClearContainer();

   iEvent.getByToken(gp_token,gp_handle); 
   iEvent.getByToken(info_token, info_handle);

   if ( not gp_handle.isValid()   ) cout<<"[GenAnalysis]::[analyze]::[ERROR] gp_handle is not valid"<<endl;
   if ( not info_handle.isValid() ) cout<<"[GenAnalysis]::[analyze]::[ERROR] info_handle is not valid"<<endl;

   // reset
   for (auto& x : container_ ) x.second=-1;

   container_["weight"] = info_handle->weights()[0];


   weights->clear();
   for(const auto&w: info_handle->weights()) weights->push_back(w);

   int n=1;
   for (const auto & gp : *gp_handle) {

	   	if (  (abs(gp.pdgId()) == 11  or abs(gp.pdgId()) == 13)
		       and gp.status() == 1
		       and n<=2
		   ){
			container_[ Form("pt%d",n) ]  =  gp.pt();
			container_[ Form("eta%d",n) ] =  gp.eta();
			container_[ Form("phi%d",n) ] =  gp.phi();
			container_[ Form("m%d",n) ]   =  gp.mass();
			container_[ Form("pdgId%d",n) ]   =  gp.pdgId();
			++n;
		}
   	}
   if (n > 2)
   {
   TLorentzVector l1 , l2;
   l1.SetPtEtaPhiM( container_["pt1"],container_["eta1"],container_["phi1"],container_["m1"]);
   l2.SetPtEtaPhiM( container_["pt2"],container_["eta2"],container_["phi2"],container_["m2"]);
   TLorentzVector Z = l1 + l2;
   container_["ptZ"] = Z.Pt();
   container_["yZ"] = Z.Rapidity();
   container_["phiZ"] = Z.Phi();
   container_["mZ"] = Z.M();
   }

   tree_->Fill();

}


// ------------ method called once each job just before starting event loop  ------------
void 
GenAnalysis::beginJob()
{
}

// ------------ method called once each job just after ending the event loop  ------------
void 
GenAnalysis::endJob() 
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GenAnalysis::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GenAnalysis);
