R__LOAD_LIBRARY($WCSIM_BUILD_DIR/lib/libWCSimRoot.so)

void convert_to_tuple(const char * fname, const char * foutname = "out.root")
{
    gStyle->SetOptStat(0);

    TChain *t = new TChain("wcsimT");
    t->Add(fname);
    std::string single_file_name = t->GetFile()->GetName();
    // Get the first file for geometry
    TFile *f = TFile::Open(single_file_name.c_str());
    if (!f->IsOpen()){
        std::cout << "Error, could not open input file: " << single_file_name << std::endl;
        return -1;
    }
    if (!f->IsOpen()) return;

    WCSimRootEvent* wcsimrootsuperevent = new WCSimRootEvent();
    t->SetBranchAddress("wcsimrootevent",&wcsimrootsuperevent);

    WCSimRootTrigger* wcsimrootevent;
    // Geometry tree - only need 1 "event"
    WCSimRootGeom *geo = 0;
    TTree *geotree = (TTree*)f->Get("wcsimGeoT");
    geotree->SetBranchAddress("wcsimrootgeom", &geo);
    std::cout << "Geotree has " << geotree->GetEntries() << " entries" << std::endl;
    if (geotree->GetEntries() == 0) {
        exit(9);
    }
    geotree->GetEntry(0);
    int nPMTs_type0=geo->GetWCNumPMT();
    std::cout << "geo has " << nPMTs_type0 << " PMTs" << std::endl;
    std::vector<int> mPMTNo(nPMTs_type0);
    std::vector<int> mPMT_PMTNo(nPMTs_type0);
    for (int i=0;i<nPMTs_type0;i++) 
    {
        WCSimRootPMT pmt;
        pmt = geo->GetPMT(i);

        mPMTNo[i] = pmt.GetmPMTNo();
        mPMT_PMTNo[i] = pmt.GetmPMT_PMTNo()-1;
    }

    TFile* fout = new TFile(foutname,"RECREATE");
    TTree* WCTEReadoutWindows = new TTree("WCTEReadoutWindows","Conversion from wcsim.root");
    std::vector<float> hit_pmt_charges;
    std::vector<float> hit_pmt_times;
    std::vector<int> hit_mpmt_slot_ids;
    std::vector<int> hit_pmt_position_ids;
    WCTEReadoutWindows->Branch("hit_pmt_charges",&hit_pmt_charges);
    WCTEReadoutWindows->Branch("hit_pmt_times",&hit_pmt_times);
    WCTEReadoutWindows->Branch("hit_mpmt_slot_ids",&hit_mpmt_slot_ids);
    WCTEReadoutWindows->Branch("hit_pmt_position_ids",&hit_pmt_position_ids);

    int count1pc = t->GetEntries()/100;
    if (count1pc==0) count1pc=1;
    for (long int nev=0;nev<t->GetEntries();nev++)
    {
        if (nev%(count1pc)==0) std::cout<<"Running "<<nev<<"-th event of total "<<t->GetEntries()<<" events"<<std::endl;

        delete wcsimrootsuperevent;
        wcsimrootsuperevent = 0;  // EXTREMELY IMPORTANT

        hit_pmt_charges.clear();
        hit_pmt_times.clear();
        hit_mpmt_slot_ids.clear();
        hit_pmt_position_ids.clear();

        t->GetEntry(nev);
        wcsimrootevent = wcsimrootsuperevent->GetTrigger(0);

        // Fill tuple
        for (int i=0; i< wcsimrootevent->GetNcherenkovdigihits() ; i++)
        {
            WCSimRootCherenkovDigiHit* wcsimrootcherenkovdigihit = (WCSimRootCherenkovDigiHit*) (wcsimrootevent->GetCherenkovDigiHits())->At(i);
            int tubeNumber     = wcsimrootcherenkovdigihit->GetTubeId()-1;
            double peForTube      = wcsimrootcherenkovdigihit->GetQ();
            double time = wcsimrootcherenkovdigihit->GetT(); // conversion from local digi time to global time

            hit_pmt_charges.push_back(peForTube);
            hit_pmt_times.push_back(time);
            hit_mpmt_slot_ids.push_back(mPMTNo[tubeNumber]);
            hit_pmt_position_ids.push_back(mPMT_PMTNo[tubeNumber]);
        }
        WCTEReadoutWindows->Fill();
    }

    std::cout<<"Save output as: "<<foutname<<std::endl;
    fout->cd();
    WCTEReadoutWindows->Write();
    fout->Close();

    f->Close();
    t->Reset();
}