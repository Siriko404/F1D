# SD-basis check (advisor blind-spot). The all-universe Table 1 (06-14) changed UncResCEO SD from
# 0.3072 (old 2-panel, UncRes-eq universe N=27,622) to 0.3010 (all-universe N=44,900). Question:
# do the LIVE Sec 2.5 economic-magnitude (FB) claims move if the denominator changes? If they round
# the same either way, the locked prose is safe and 0.3072 is just a legitimate different-sample SD.
# Betas: full-precision convergent-validity coefs (industry-FE col, the one Sec 2.5 leads with).
# IV SDs: from the current all-universe Table 1 (_tables_from_bible.tex).
betas = {"PRisk": 0.0001084, "US_EPU_log": 0.01241, "GEPU_log": 0.01799}
iv_sd = {"PRisk": 146.5189, "US_EPU_log": 0.3661, "GEPU_log": 0.3672}
labels = {"PRisk": "political risk", "US_EPU_log": "US policy uncertainty", "GEPU_log": "global policy uncertainty"}
draft_says = {"PRisk": "5%", "US_EPU_log": "1.5%", "GEPU_log": "2.2%"}

SD_all_universe = 0.3010   # current Table 1, N=44,900
SD_estimation   = 0.3072   # old UncRes-eq universe, N=27,622 (the run-up estimation sample)

print(f"{'IV':12} {'effect':>9} | {'% of 0.3010':>12} {'% of 0.3072':>12} | draft says")
print("-" * 64)
for k in betas:
    eff = betas[k] * iv_sd[k]
    pa = 100 * eff / SD_all_universe
    pe = 100 * eff / SD_estimation
    print(f"{k:12} {eff:9.5f} | {pa:11.2f}% {pe:11.2f}% | {draft_says[k]}")

print("\nRun-up magnitude (old Sec 3 prose, 'fifteen percent of a SD'): cash UncRes beta = 0.0461")
print(f"   0.0461 / 0.3010 = {100*0.0461/0.3010:.1f}%   |   0.0461 / 0.3072 = {100*0.0461/0.3072:.1f}%")

print("\nVERDICT: if both columns round to the draft's stated magnitudes, the locked Sec 2.5 FB is")
print("SAFE regardless of SD basis, and 0.3072 is a legitimate estimation-sample SD (not a stale headline).")
