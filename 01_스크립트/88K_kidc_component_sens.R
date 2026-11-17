# 88K_kidc_component_sens.R — 32호 KIDC: 판정 성분(시도·연도 eGFR<60 비율, 요단백 +1 이상 비율)을 더한 주모형 민감도(2026-11-17).
#  88g_sens_suite_kidc.R의 준비부만 실행(GROUP=0) 뒤 K1(두 성분)·K2(요단백만)·K3(eGFR만) 적합. 출력 results_std3/S41_part_K*.csv
Sys.setenv(GROUP="0"); ff<-sub("--file=","",grep("--file=",commandArgs(),value=TRUE)); source(file.path(dirname(ff),"88g_sens_suite_kidc.R"))
X<-rdp("S41_panel_comp.csv"); CC<-c("prov_egfr_z","prov_dip_z"); d<-mrg(DD,X,CC); stopifnot(!anyNA(d[,CC]))
for(k in list(list("K1_prov_components",CC),list("K2_prov_dipstick","prov_dip_z"),list("K3_prov_egfr","prov_egfr_z"))){
  if(dn(k[[1]]))next; summ(k[[1]],"outcome_components",fitX(c(MAINV,k[[2]]),d),d,paste("+ province-year",paste(k[[2]],collapse="+")),vars=c(MAINV,k[[2]]))}
