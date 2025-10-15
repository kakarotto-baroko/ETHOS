window.EOS_CFG = {
  data: {
    board:   "/output/board.json",
    stages:  "/output/stages.json",
    sensors: "/output/sensors.json",
    feedback:"/output/feedback.json",
    resonance:"/output/resonance.json",
    x_objective:"/output/x_objective.json",
    x_policy:"/output/x_policy.json"
  },
  palette: { bucket:{ "1000x":"blue", "10000x":"red" } },
  labels: { stages:["S1","S2","S3","S4","S5"] },
  s5BadgeText: (regime)=>{
    if(!regime) return "S5: —";
    const r = regime?.s5_regime || regime?.regime || regime;
    return "S5: "+String(r);
  }
};