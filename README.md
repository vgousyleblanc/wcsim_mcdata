A first installation of WCsim is required to run any of those files. This can be done with a software container and is well documented in https://github.com/WCTE/SoftwareContainer. 

The following description provides the tips for running a comparison of WCTE data with WCsim.<br/>

1-A mapping needs to be applied between WCTE PMT and WCSim<br/>
2- Make sure to reference the correct source file present in WCSim/build/this_wcsim.sh <br/>
3- The WCSim executable is in WCSim/build/install/bin/WCSim and needs the macro and tuning parameters <br/>
4- The notebook and event display of WCTE sim will expect the output directly of convert_to_tuple.c w,hich can be used with root to compile. <br/>

The notebook needs dependencies which are all described in the helpful tips to work with WCTE data on wcte.canada. (Geometry, TimeCal, EventDisplay).  <br/>



