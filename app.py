# =========================================================
# 🌱 일반계좌 대시보드 상세페이지
# =========================================================
elif st.session_state.current_view == '일반계좌':
    st.markdown("<h3 style='margin-top: 5px; margin-bottom: 25px;'>🚀 Andy lee님 [일반계좌] 통합 대시보드</h3>", unsafe_allow_html=True)

    if not isinstance(g_data, dict):
        st.warning("데이터가 올바르지 않습니다. 좌측 사이드바의 업데이트 버튼을 눌러주세요.")
        st.stop()

    nm_table = {'DOM1': '키움증권(국내Ⅰ)', 'DOM2': '삼성증권(국내Ⅱ)', 'USA1': '키움증권(해외Ⅰ)', 'USA2': '키움증권(해외Ⅱ)'}
    nm_table_expander = {'DOM1': '키움증권(국내Ⅰ) : 6312-5329', 'DOM2': '삼성증권(국내Ⅱ) : 7162669785-01', 'USA1': '키움증권(해외Ⅰ) : 6312-5329', 'USA2': '키움증권(해외Ⅱ) : 6443-5993'}
    principals = {"DOM1": 110963075, "DOM2": 5208948, "USA1": 257915999, "USA2": 7457930}
    GEN_ACC_ORDER = ['DOM1', 'DOM2', 'USA1', 'USA2']
    
    t_asset = sum(safe_float(g_data[k].get("총자산_KRW", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
    t_profit = sum(safe_float(g_data[k].get("총수익_KRW", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
    t_buy_total = sum(safe_float(g_data[k].get("매입금액_KRW", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
    
    t_prof_7ago = sum(safe_float(g_data[k].get("평가손익(7일전)", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
    t_prof_15ago = sum(safe_float(g_data[k].get("평가손익(15일전)", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
    t_prof_30ago = sum(safe_float(g_data[k].get("평가손익(30일전)", 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict))
    
    t_diff_7 = t_profit - t_prof_7ago; t_diff_15 = t_profit - t_prof_15ago; t_diff_30 = t_profit - t_prof_30ago
    t_original_sum = sum(principals.values())
    t_rate = (t_profit / t_original_sum * 100) if t_original_sum > 0 else 0

    cash_total = 0; dom_total = 0; ovs_total = 0
    dom_items = []; ovs_items = []; acc_1d_diff = {}
    
    for k in GEN_ACC_ORDER:
        acc_1d_diff[k] = 0
        if k in g_data and isinstance(g_data[k], dict):
            is_usa = 'USA' in k
            fx = safe_float(g_data.get('환율', 1443.1)) if is_usa else 1
            details = g_data[k].get('상세', [])
            if isinstance(details, list):
                for item in details:
                    if isinstance(item, dict) and item.get('종목명') != '[ 합  계 ]':
                        it_copy = item.copy(); it_copy['계좌'] = nm_table[k]; it_copy['_k'] = k
                        val_krw = safe_float(item.get('총자산', 0)) * fx
                        nm = str(item.get('종목명', ''))
                        if nm == '예수금' or '현금' in nm: cash_total += val_krw
                        else:
                            c_p = safe_float(it_copy.get('현재가', 0)); qty = safe_float(it_copy.get('수량', 0)); d_rate = safe_float(it_copy.get('전일비', 0))
                            if c_p > 0 and d_rate != 0: acc_1d_diff[k] += ((c_p - (c_p / (1 + d_rate / 100))) * fx * qty)
                            if is_usa: ovs_total += val_krw; ovs_items.append(it_copy)
                            else: dom_total += val_krw; dom_items.append(it_copy)

    t_diff = sum(acc_1d_diff.values())
    goal_amount = 1500000000; progress_pct = (t_asset / goal_amount) * 100 if goal_amount > 0 else 0

    all_tradeable = dom_items + ovs_items
    rise_cnt = sum(1 for it in all_tradeable if safe_float(it.get('전일비', 0)) > 0.5)
    fall_cnt = sum(1 for it in all_tradeable if safe_float(it.get('전일비', 0)) < -0.5)
    flat_cnt = len(all_tradeable) - rise_cnt - fall_cnt
    
    dom_best = sorted(dom_items, key=lambda x: safe_float(x.get('수익률(%)', 0)), reverse=True)[:5]
    dom_worst = sorted([it for it in dom_items if safe_float(it.get('수익률(%)', 0)) < 5.0], key=lambda x: safe_float(x.get('수익률(%)', 0)))[:5]
    ovs_best = sorted(ovs_items, key=lambda x: safe_float(x.get('수익률(%)', 0)), reverse=True)[:5]
    ovs_worst = sorted([it for it in ovs_items if safe_float(it.get('수익률(%)', 0)) < 5.0], key=lambda x: safe_float(x.get('수익률(%)', 0)))[:5]

    total_for_bar = max(1, t_asset)
    p_dom1 = safe_float(g_data.get('DOM1', {}).get('총자산_KRW', 0)) / total_for_bar * 100 if isinstance(g_data.get('DOM1'), dict) else 0
    p_dom2 = safe_float(g_data.get('DOM2', {}).get('총자산_KRW', 0)) / total_for_bar * 100 if isinstance(g_data.get('DOM2'), dict) else 0
    p_usa1 = safe_float(g_data.get('USA1', {}).get('총자산_KRW', 0)) / total_for_bar * 100 if isinstance(g_data.get('USA1'), dict) else 0
    p_usa2 = safe_float(g_data.get('USA2', {}).get('총자산_KRW', 0)) / total_for_bar * 100 if isinstance(g_data.get('USA2'), dict) else 0

    def render_bar(p, color): return f"<div style='width: {p}%; background-color: {color}; height: 100%; display: flex; align-items: center; justify-content: center; position: relative;'><span style='position: absolute; font-size: 13px; color: #333; z-index: 10; white-space: nowrap;'>{p:.0f}%</span></div>" if p > 0 else ""

    acc_rates = sorted([(k, (safe_float(g_data[k].get('총수익_KRW',0)) / principals[k] * 100 if principals[k]>0 else 0)) for k in GEN_ACC_ORDER if k in g_data and isinstance(g_data[k], dict)], key=lambda x: x[1], reverse=True)
    best_acc_name = nm_table.get(acc_rates[0][0], "전체") if acc_rates else "전체"

    zappa_html = f"<div style='font-size: 14.5px; line-height: 1.85; color: #444; padding-left: 0px;'><div style='margin-bottom: 22px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> [통합] 계좌 현황 요약</span><div>현재 전체 포트폴리오 총 손익은 <span class='{col(t_profit)}'><strong>{fmt(t_profit, True)}</strong></span> (<span class='{col(t_rate)}'><strong>{fmt_p(t_rate)}</strong></span>) 이며, <strong>{best_acc_name}</strong> 계좌가 계좌별 수익률 1위를 기록 중입니다. 총 <strong>{len(all_tradeable)}개</strong> 종목 중 0.5% 초과 상승종목은 <strong>{rise_cnt}개</strong>, 하락종목은 <strong>{fall_cnt}개</strong>, 보합종목은 <strong>{flat_cnt}개</strong> 입니다.</div></div><div style='margin-bottom: 15px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> [국내] 시황 및 전망</span><div>최근 국내 시장은 <strong>{short_name(dom_best[0]['종목명']) if dom_best else '국내 우량주'}</strong> 등 일부 우수 종목이 상승을 견인하고 있으나, <strong>{short_name(dom_worst[0]['종목명']) if dom_worst else '일부 조정주'}</strong> 등은 조정을 받고 있습니다. 실적 기반의 리밸런싱을 권고합니다.</div></div><div style='margin-bottom: 0px;'><span style='color:#111; font-size:16px; font-weight:bold; display:flex; align-items:center; gap:6px; margin-bottom:6px;'><span style='font-size:11px;'>🔵</span> [해외] 시황 및 전망</span><div>미국 증시는 <strong>{short_name(ovs_best[0]['종목명']) if ovs_best else '빅테크 우량주'}</strong> 위주로 긍정적 흐름을 보이나, <strong>{short_name(ovs_worst[0]['종목명']) if ovs_worst else '단기 하락주'}</strong> 등 부진 섹터는 비중 조절이 필요합니다. 현재 <strong>{(cash_total/t_asset*100) if t_asset>0 else 0:.1f}%</strong>인 현금성(예수금) 비중을 유동적으로 관리하시기 바랍니다.</div></div></div>"

    st.markdown("<div class='sub-title' style='margin-bottom: 15px;'>💡 [일반계좌] 자산 현황 요약</div>", unsafe_allow_html=True)
    
    p_cash_donut = (cash_total/t_asset*100) if t_asset>0 else 0
    p_ovs_donut = (ovs_total/t_asset*100) if t_asset>0 else 0
    p_dom_donut = (dom_total/t_asset*100) if t_asset>0 else 0
    
    donut_css = f"background: conic-gradient(#ffffff 0% {p_cash_donut}%, #d9d9d9 {p_cash_donut}% {p_cash_donut+p_ovs_donut}%, #8c8c8c {p_cash_donut+p_ovs_donut}% 100%);"
    donut_html = f"<div style='position: relative; width: 120px; height: 120px; border-radius: 50%; {donut_css} box-shadow: inset 0 0 8px rgba(0,0,0,0.1); border: 1px solid #d0d0d0; flex-shrink: 0; margin: 0 auto;'><div style='position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 35%; height: 35%; background-color: #fffdf2; border-radius: 50%; box-shadow: 0 0 5px rgba(0,0,0,0.05);'></div><div style='position: absolute; top: 0%; left: 50%; transform: translateX(-50%); font-size: 12.5px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_cash_donut:.0f}%<br>현금성자산</div><div style='position: absolute; top: 55px; right: -15px; font-size: 14px; color: #333; text-align: center; line-height: 1.1; font-weight: bold;'>{p_ovs_donut:.0f}%<br>해외투자</div><div style='position: absolute; bottom: 42px; left: -20px; font-size: 14px; color: #fff; font-weight: bold; text-align: center; line-height: 1.1; text-shadow: 0px 0px 3px rgba(0,0,0,0.5);'>{p_dom_donut:.0f}%<br>국내투자</div></div>"

    html_parts = []
    html_parts.append("<div style='text-align: right; font-size: 13px; color: #555; font-weight: bold; margin-bottom: 5px;'>단위 : 원화(KRW)</div><div class='insight-container'><div class='insight-left'><div class='card-main'><div style='display: flex; gap: 15px; align-items: stretch; margin-bottom: auto;'><div style='flex: 0 0 38%; display: flex; flex-direction: column; align-items: center;'><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 15px; width:100%; text-align:left;'>총 자산</div>")
    html_parts.append(donut_html)
    html_parts.append(f"<div style='font-size: 13.5px; color: #333; font-weight: bold; margin-top: 14px;'><span style='font-size: 12.5px; color: #666;'>원금</span> : {fmt(t_original_sum)}</div></div><div style='flex: 1; display: flex; flex-direction: column; justify-content: flex-start; padding-top: 5px;'><div class='card-inner' style='padding: 10px 12px; margin-bottom: 8px;'><div style='font-size: 24px; font-weight: 700 !important; color: #111; letter-spacing: normal; line-height: 1; margin-bottom: 6px;'>{fmt(t_asset)}<span style='font-size: 13.5px; font-weight: normal; margin-left: 3px; letter-spacing: normal;'>KRW</span></div><div style='font-size: 13.5px; color: #777; font-weight: normal; line-height: 1;'>[ 전일비 <span class='{col(t_diff)}'>{fmt(t_diff, True)}</span> / 전주비 <span class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</span> ]</div></div><div style='display: grid; grid-template-columns: auto auto; row-gap: 12px; column-gap: 30px; justify-content: end; align-items: baseline; width: 100%; padding-right: 12px; margin-top: 8px;'><div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>평가금액</div><div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(t_asset - cash_total)}</div><div style='color: #777; font-size: 14px; text-align: right; line-height: 20px;'>현금성(예수금)</div><div style='color: #111; font-size: 18px; font-weight: 400; text-align: right; line-height: 20px;'>{fmt(cash_total)}</div><div style='color: #777; font-size: 14px; font-weight: normal; text-align: right; line-height: 20px;'>총 손익</div><div style='text-align: right;'><div style='font-size: 18px; font-weight: 600; line-height: 1;' class='{col(t_profit)}'>{fmt(t_profit, True)}</div><div style='font-size: 13.5px; font-weight: 600; margin-top: 3px; line-height: 1;' class='{col(t_rate)}'>{fmt_p(t_rate)}</div></div></div></div></div><div style='margin-top: 20px;'><div style='display: flex; height: 20px; width: 100%; border-radius: 4px; border: 1px solid #ccc; margin-bottom: 6px; overflow: hidden;'>{render_bar(p_dom1, '#b4a7d6')}{render_bar(p_dom2, '#f4b183')}{render_bar(p_usa1, '#a9d18e')}{render_bar(p_usa2, '#ffd966')}</div><div style='display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: #777; padding: 0 2px; margin-bottom: 16px;'><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#b4a7d6; border-radius:3px;'></div>키움증권(국내Ⅰ)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#f4b183; border-radius:3px;'></div>삼성증권(국내Ⅱ)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#a9d18e; border-radius:3px;'></div>키움증권(해외Ⅰ)</div><div style='display: flex; align-items: center; gap: 4px;'><div style='width:12px; height:12px; background-color:#ffd966; border-radius:3px;'></div>키움증권(해외Ⅱ)</div></div><div style='padding: 10px 15px; background: rgba(255,255,255,0.5); border-radius: 10px; border: 1px solid #e8dbad;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;'><span style='font-size: 14px; color: #777; font-weight: normal;'>🎯 주식투자 자산 15억 프로젝트</span><div style='text-align: right;'><span style='font-size: 14px; font-weight: bold; color: #4a90e2;'>{progress_pct:.1f}%</span></div></div><div style='width: 100%; height: 6px; background-color: #e2e2e2; border-radius: 3px; overflow: hidden;'><div style='width: {progress_pct}%; height: 100%; background: linear-gradient(90deg, #9bc2e6, #4a90e2);'></div></div></div></div></div></div><div class='insight-right'><div class='grid-2x2'>")
    for k in GEN_ACC_ORDER:
        if k in g_data and isinstance(g_data[k], dict):
            a = g_data[k]
            acc_num_map = {'DOM1': '[ 6312-5329 ]', 'DOM2': '[ 7162669785-01 ]', 'USA1': '[ 6312-5329 ]', 'USA2': '[ 6443-5993 ]'}
            details = a.get('상세', [])
            item_count = len([i for i in details if isinstance(i, dict) and str(i.get('종목명', '')) not in ['[ 합  계 ]', '예수금', '현금성자산', '현금성자산(예수금)']]) if isinstance(details, list) else 0
            
            html_parts.append(f"<a href='#gen_detail_section' style='text-decoration:none; color:inherit; display:block; height:100%;'><div class='card-sub' style='height:100%; justify-content:space-between;'><div><div style='text-align: right; font-size: 13.5px; color: #666; font-weight: normal; margin-bottom: -2px; line-height: 1;'>{acc_num_map[k]}</div><div style='font-size: 18px; font-weight: bold; color: #111; margin-bottom: 2px;'>{nm_table[k]}</div><div style='border-bottom: 1px solid #eee; margin-bottom: 6px; margin-top: 2px;'></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 자산</span><span style='font-size: 16px; color: #111; font-weight: normal;'>{fmt(safe_float(a.get('총자산_KRW', 0)))}</span></div><div style='display: flex; justify-content: space-between; align-items: baseline; margin-bottom: 4px;'><span style='font-size: 14.5px; color: #666; font-weight: normal;'>총 손익</span><div style='text-align: right; line-height: 1.2;'><div class='{col(a.get('총수익_KRW', 0))}' style='font-size: 16px; font-weight: normal;'>{fmt(safe_float(a.get('총수익_KRW', 0)), True)}</div><div class='{col(safe_float(a.get('총수익_KRW',0))/principals[k]*100 if principals[k] else 0)}' style='font-size: 14px; font-weight: normal; margin-top: 1px;'>{fmt_p(safe_float(a.get('총수익_KRW',0))/principals[k]*100 if principals[k] else 0)}</div></div></div></div><div style='font-size: 13.5px; color: #666; font-weight: normal; margin-top: auto; padding-top: 2px; display: flex; justify-content: space-between; align-items: baseline;'><span>* <span style='font-size: 12.5px;'>원금</span> : {fmt(principals[k])}</span><span><span style='font-size: 16px; font-weight: bold; color: #111;'>{item_count}</span> 종목</span></div></div></a>")
    html_parts.append("</div></div></div>")
    
    html_parts.append("<div class='insight-bottom-box' style='display: flex; gap: 20px; align-items: stretch;'><div style='flex: 1; padding-right: 15px; border-right: 1px solid #eaeaea;'><div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 [국내] 손익률 우수종목</div><table class='main-table' style='margin-bottom: 20px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>")
    for idx, it in enumerate(dom_best):
        c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
        orig_nm = it.get('종목명', ''); disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
        nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
        html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
    html_parts.append("</table><div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 [국내] 손익률 부진종목</div><table class='main-table' style='margin-bottom: 25px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익</th><th>등락률</th></tr>")
    for idx, it in enumerate(dom_worst):
        c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
        orig_nm = it.get('종목명', ''); disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
        nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
        html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(it.get('평가손익', 0))}'>{fmt(it.get('평가손익', 0), True)}</td>{diff_html}</tr>")
    html_parts.append("</table><hr style='border:0; border-top:1px dashed #ddd; margin: 25px 0;'>")
    
    fx_rate = safe_float(g_data.get('환율', 1443.1))
    html_parts.append("<div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; letter-spacing: normal;'>📈 [해외] 손익률 우수종목</div><table class='main-table' style='margin-bottom: 20px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익(KRW)</th><th>등락률</th></tr>")
    for idx, it in enumerate(ovs_best):
        c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) * fx_rate if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
        orig_nm = it.get('종목명', ''); disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
        nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
        html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(safe_float(it.get('평가손익', 0))*fx_rate)}'>{fmt(safe_float(it.get('평가손익', 0))*fx_rate, True)}</td>{diff_html}</tr>")
    html_parts.append("</table><div style='font-size: 17px; font-weight: bold; color: #111; margin-bottom: 8px; margin-top: 15px; letter-spacing: normal;'>📉 [해외] 손익률 부진종목</div><table class='main-table' style='margin-bottom: 0px;'><tr><th style='width:40px;'></th><th>종목명</th><th>손익률</th><th>평가손익(KRW)</th><th>등락률</th></tr>")
    for idx, it in enumerate(ovs_worst):
        c_p = safe_float(it.get('현재가', 0)); d_rate = safe_float(it.get('전일비', 0)); diff_amt = (c_p - (c_p / (1 + d_rate / 100))) * fx_rate if c_p > 0 and d_rate != 0 else 0
        d_class = col(d_rate); diff_html = f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{fmt(diff_amt, True)}</div><div class='{d_class}' style='font-size:13px;'>{fmt_p(d_rate)}</div></td>"
        acc_tag = f"<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({it.get('계좌', '')})</span>"
        orig_nm = it.get('종목명', ''); disp_nm = short_name(orig_nm); logo_html = get_logo_html(orig_nm)
        nm_html = f"<td style='line-height:1.3; padding-top:6px; padding-bottom:6px; text-align:left; padding-left:10px;'>{logo_html}{disp_nm}{acc_tag}</td>"
        html_parts.append(f"<tr><td>{idx+1}</td>{nm_html}<td class='{col(it.get('수익률(%)', 0))}'>{fmt_p(it.get('수익률(%)', 0))}</td><td class='{col(safe_float(it.get('평가손익', 0))*fx_rate)}'>{fmt(safe_float(it.get('평가손익', 0))*fx_rate, True)}</td>{diff_html}</tr>")
    html_parts.append("</table></div><div style='flex: 1.1; padding-left: 5px;'><div style='display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px; border-bottom: 1px solid #eee; padding-bottom: 8px;'><div style='font-size: 18px; font-weight: bold; color: #111; letter-spacing: normal;'>💡 시황 및 향후 전망</div><div style='font-size: 13.5px; color: #888;'>[ -0.5%p < 보합 < +0.5%p ]</div></div>{zappa_html}</div></div>")
    st.markdown("".join(html_parts), unsafe_allow_html=True)

    unit_html = "<div style='text-align:right;font-size:13px;color:#555;margin-bottom:5px;font-weight:bold;'>단위 : 원화(KRW)</div>"
    st.markdown("<div class='sub-title'>📊 [1] 투자원금 대비 자산 현황</div>", unsafe_allow_html=True)
    st.markdown(f"<div style='margin-bottom:10px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(t_profit)}'>{fmt(t_profit, True)} ({fmt_p(t_rate)})</span></div></div>", unsafe_allow_html=True)

    h1_table = "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>투자원금</th></tr><tr><th class='th-week'>7일전</th><th class='th-week'>15일전</th><th class='th-week'>30일전</th></tr>"
    h1 = [unit_html, h1_table, f"<tr class='sum-row'><td>[ 합  계 ]</td><td>{fmt(t_asset)}</td><td class='{col(t_profit)}'>{fmt(t_profit, True)}</td><td class='{col(t_prof_7ago)}'>{fmt(t_prof_7ago, True)}</td><td class='{col(t_prof_15ago)}'>{fmt(t_prof_15ago, True)}</td><td class='{col(t_prof_30ago)}'>{fmt(t_prof_30ago, True)}</td><td class='{col(t_rate)}'>{fmt_p(t_rate)}</td><td>{fmt(t_original_sum)}</td></tr>"]
    for k in GEN_ACC_ORDER:
        if k in g_data and isinstance(g_data[k], dict):
            a = g_data[k]
            a_tot = safe_float(a.get('총자산_KRW',0)); a_prof = safe_float(a.get('총수익_KRW',0))
            p7 = safe_float(a.get('평가손익(7일전)',0)); p15 = safe_float(a.get('평가손익(15일전)',0)); p30 = safe_float(a.get('평가손익(30일전)',0))
            h1.append(f"<tr><td>{nm_table[k]}</td><td>{fmt(a_tot)}</td><td class='{col(a_prof)}'>{fmt(a_prof, True)}</td><td class='{col(p7)}'>{fmt(p7, True)}</td><td class='{col(p15)}'>{fmt(p15, True)}</td><td class='{col(p30)}'>{fmt(p30, True)}</td><td class='{col(a_prof/principals[k]*100 if principals[k] else 0)}'>{fmt_p(a_prof/principals[k]*100 if principals[k] else 0)}</td><td>{fmt(principals[k])}</td></tr>")
    h1.append("</table>")
    st.markdown("".join(h1), unsafe_allow_html=True)

    ag_tot = t_asset - t_buy_total
    ay_tot = (ag_tot / t_buy_total * 100) if t_buy_total > 0 else 0
    st.markdown("<div class='sub-title'>📈 [2] 매입금액 대비 자산 현황</div>", unsafe_allow_html=True)
    st.markdown(f"<div class='summary-text'>● 총 자산 : <span class='summary-val'>{fmt(t_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(ag_tot)}'>{fmt(ag_tot, True)} ({fmt_p(ay_tot)})</span></div>", unsafe_allow_html=True)

    h2_table = "<table class='main-table'><tr><th rowspan='2'>계좌 구분</th><th rowspan='2'>총 자산</th><th rowspan='2' class='th-eval'>평가손익</th><th colspan='3' class='th-blank'>&nbsp;</th><th rowspan='2'>손익률</th><th rowspan='2'>매입금액</th></tr><tr><th class='th-week'>전일비</th><th class='th-week'>전주비</th><th class='th-week'>전월비</th></tr>"
    h2 = [unit_html, h2_table, f"<tr class='sum-row'><td>[ 합  계 ]</td><td>{fmt(t_asset)}</td><td class='{col(ag_tot)}'>{fmt(ag_tot, True)}</td><td class='{col(t_diff)}'>{fmt(t_diff, True)}</td><td class='{col(t_diff_7)}'>{fmt(t_diff_7, True)}</td><td class='{col(t_diff_30)}'>{fmt(t_diff_30, True)}</td><td class='{col(ay_tot)}'>{fmt_p(ay_tot)}</td><td>{fmt(t_buy_total)}</td></tr>"]
    
    for k in GEN_ACC_ORDER:
        if k in g_data and isinstance(g_data[k], dict):
            a = g_data[k]
            buy_krw = safe_float(a.get('매입금액_KRW', 0))
            ag_acc = safe_float(a.get('총자산_KRW', 0)) - buy_krw
            ay_acc = (ag_acc / buy_krw * 100) if buy_krw > 0 else 0
            a_prof = safe_float(a.get('총수익_KRW', 0))
            diff_7_acc = a_prof - safe_float(a.get('평가손익(7일전)', 0))
            diff_30_acc = a_prof - safe_float(a.get('평가손익(30일전)', 0))
            h2.append(f"<tr><td>{nm_table[k]}</td><td>{fmt(safe_float(a.get('총자산_KRW',0)))}</td><td class='{col(ag_acc)}'>{fmt(ag_acc, True)}</td><td class='{col(acc_1d_diff.get(k, 0))}'>{fmt(acc_1d_diff.get(k, 0), True)}</td><td class='{col(diff_7_acc)}'>{fmt(diff_7_acc, True)}</td><td class='{col(diff_30_acc)}'>{fmt(diff_30_acc, True)}</td><td class='{col(ay_acc)}'>{fmt_p(ay_acc)}</td><td>{fmt(buy_krw)}</td></tr>")
    h2.append("</table>")
    st.markdown("".join(h2), unsafe_allow_html=True)

    st.markdown("<div id='gen_detail_section' style='padding-top: 20px; margin-top: -20px;'></div><div class='sub-title'>🔍 [3] 계좌별 상세 내역</div>", unsafe_allow_html=True)
    b1, b2, b3, b4, b5, b6 = st.columns(6)
    with b1:
        st.markdown("<span id='zappa-floating-menu'></span>", unsafe_allow_html=True)
        lbl1 = "📊정렬 [ 초기화(●)" if st.session_state.gen_sort_mode == 'init' else "📊정렬 [ 초기화(○)"
        if st.button(lbl1, type="primary" if st.session_state.gen_sort_mode == 'init' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'init')): pass
    with b2:
        lbl2 = "총자산(▼)" if st.session_state.gen_sort_mode == 'asset' else "총자산(▽)"
        if st.button(lbl2, type="primary" if st.session_state.gen_sort_mode == 'asset' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'asset')): pass
    with b3:
        lbl3 = "평가손익(▼)" if st.session_state.gen_sort_mode == 'profit' else "평가손익(▽)"
        if st.button(lbl3, type="primary" if st.session_state.gen_sort_mode == 'profit' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'profit')): pass
    with b4:
        lbl4 = "손익률(▼) ]" if st.session_state.gen_sort_mode == 'rate' else "손익률(▽) ]"
        if st.button(lbl4, type="primary" if st.session_state.gen_sort_mode == 'rate' else "secondary", on_click=lambda: setattr(st.session_state, 'gen_sort_mode', 'rate')): pass
    with b5:
        lbl5 = "↕️등락률[-]" if st.session_state.gen_show_change_rate else "↕️등락률[+]"
        if st.button(lbl5, type="primary" if st.session_state.gen_show_change_rate else "secondary", on_click=lambda: setattr(st.session_state, 'gen_show_change_rate', not st.session_state.gen_show_change_rate)): pass
    with b6:
        lbl6 = "💻종목코드[-]" if st.session_state.show_code else "💻종목코드[+]"
        if st.button(lbl6, type="primary" if st.session_state.show_code else "secondary", on_click=lambda: setattr(st.session_state, 'show_code', not st.session_state.show_code)): pass

    st.markdown("<br>", unsafe_allow_html=True)

    for k in GEN_ACC_ORDER:
        if k in g_data and isinstance(g_data[k], dict):
            a = g_data[k]
            is_usa = 'USA' in k
            with st.expander(f"📂 [ {nm_table_expander[k]} ] 종목별 현황", expanded=False):
                details = a.get('상세', [])
                
                if k == 'DOM1':
                    for i in details:
                        if isinstance(i, dict) and '예수금' in str(i.get('종목명','')): 
                            i['총자산'] = 132563; break
                elif k == 'USA2':
                    has_cash = False
                    for i in details:
                        if isinstance(i, dict) and '예수금' in str(i.get('종목명','')): 
                            i['총자산'] = 0; has_cash = True; break
                    if not has_cash: 
                        details.append({'종목명': '예수금', '비중': 0, '총자산': 0, '평가손익': 0, '수익률(%)': 0, '전일비': 0, '수량': '-', '매입가': '-', '현재가': '-'})

                s_data = next((i for i in details if isinstance(i, dict) and i.get('종목명') == "[ 합  계 ]"), {}) if isinstance(details, list) else {}
                s_rate = s_data.get('수익률(%)', 0)
                curr_asset = safe_float(a.get('총자산_KRW', 0)); a_prof = safe_float(a.get('총수익_KRW', 0))
                rate_val = safe_float(g_data.get('환율', 1443.1))
                
                if is_usa:
                    st.markdown(f"<div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:0px;'><div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(curr_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(a_prof)}'>{fmt(a_prof, True)} ({fmt_p(s_rate)})</span></div></div>", unsafe_allow_html=True)
                    u_c1, u_c2 = st.columns([8.8, 1.2])
                    with u_c2:
                        currency_mode = st.selectbox("표기단위", options=["[원화(KRW)]", "[달러(USD)]", "[원화/달러]"], index=2, label_visibility="collapsed", key=f"curr_sel_box_{k}")
                else:
                    currency_mode = "[원화(KRW)]"
                    st.markdown(f"""
                    <div style='display:flex; justify-content:space-between; align-items:flex-end; margin-bottom:10px;'>
                        <div class='summary-text' style='margin-bottom:0;'>● 총 자산 : <span class='summary-val'>{fmt(curr_asset)}</span> KRW / 총 손익 : <span class='summary-val {col(a_prof)}'>{fmt(a_prof, True)} ({fmt_p(s_rate)})</span></div>
                        <div style='text-align:right; font-size:12.5px; color:#888; font-weight:bold;'>단위 : 원화(KRW)</div>
                    </div>
                    """, unsafe_allow_html=True)
                
                code_th = "<th>종목코드</th>" if st.session_state.show_code else ""
                
                # 💡 [테이블 헤더 패치] '종목명' 헤더 부분 가운데 정렬
                h3 = [f"<table class='main-table'><tr><th style='text-align:center;'>종목명</th>{code_th}<th>비중</th><th>총 자산</th><th>평가손익</th><th>손익률</th><th>주식수</th><th>매입가</th><th>현재가</th>" + ("<th>등락률</th>" if st.session_state.gen_show_change_rate else "") + "</tr>"]
                
                items = [i for i in details if isinstance(i, dict) and i.get('종목명') not in ["[ 합  계 ]", "예수금"]] if isinstance(details, list) else []
                cash_item = next((i for i in details if isinstance(i, dict) and i.get('종목명') == "예수금"), {"종목명": "예수금", "총자산": 0, "평가손익": 0, "수익률(%)": 0, "수량": "-", "매입가": "-", "현재가": "-", "전일비": 0}) if isinstance(details, list) else {}
                
                if st.session_state.gen_sort_mode == 'asset': items.sort(key=lambda x: safe_float(x.get('총자산', 0)), reverse=True)
                elif st.session_state.gen_sort_mode == 'profit': items.sort(key=lambda x: safe_float(x.get('평가손익', 0)), reverse=True)
                elif st.session_state.gen_sort_mode == 'rate': items.sort(key=lambda x: safe_float(x.get('수익률(%)', 0)), reverse=True)
                
                def fmt_dual(val_raw, sign=False):
                    if val_raw == '-': return '-'
                    if not is_usa: return fmt(val_raw, sign)
                    val_krw = safe_float(val_raw) * rate_val
                    s_krw = fmt(val_krw, sign); s_usd = fmt(safe_float(val_raw), sign, decimal=4)
                    if currency_mode == "[원화/달러]": return f"{s_krw}<br><span style='font-size:11.5px; color:#888; font-weight:normal;'>({s_usd})</span>"
                    elif currency_mode == "[달러(USD)]": return s_usd
                    else: return s_krw

                for i in ([s_data] + items + [cash_item]):
                    if not i: continue
                    if i.get('종목명') == "예수금" and safe_float(i.get('총자산', 0)) == 0 and k != 'USA2' and safe_float(s_data.get('총자산', 0)) > 0: 
                        continue
                        
                    is_s = (i.get('종목명') == "[ 합  계 ]")
                    row = f"<tr class='sum-row'>" if is_s else "<tr>"
                    
                    # 💡 [코드 박스 에러 패치] 줄바꿈(\n) 및 백틱(`) 정화 작업 추가
                    raw_nm = '피그마' if i.get('종목명') == 'Figma' else str(i.get('종목명', ''))
                    orig_nm = raw_nm.replace('\n', ' ').replace('\r', '').replace('`', '').strip()
                    
                    # 💡 [가운데 정렬 패치] 합계와 일반 종목은 center, 예수금은 left 유지
                    if is_s: 
                        row += f"<td style='text-align:center; padding-left:0px;'>{orig_nm}</td>"
                    elif '예수금' in orig_nm or '현금' in orig_nm: 
                        row += f"<td style='text-align:left; padding-left:15px;'><span style='font-size:16px; margin-right:6px; vertical-align:middle;'>💵</span>{orig_nm}</td>"
                    else: 
                        row += f"<td style='text-align:center; padding-left:0px;'>{get_logo_html(orig_nm)}{orig_nm}</td>"
                    
                    if st.session_state.show_code: row += f"<td>{'-' if is_s or i.get('코드','-')=='-' else i.get('코드', '')}</td>"
                    
                    ia = fmt_dual(i.get('총자산', 0)); ip = fmt_dual(i.get('평가손익', 0), True)
                    ibuy = fmt_dual(i.get('매입가', '-')); icurr = fmt_dual(i.get('현재가', '-'))
                    s_tot = safe_float(s_data.get('총자산', 1))
                    pct = (safe_float(i.get('총자산', 0)) / s_tot * 100) if s_tot > 0 else 0
                    
                    d_rate = safe_float(i.get('전일비', 0)); curr_price = safe_float(i.get('현재가', 0))
                    diff_amt_raw = (curr_price - (curr_price / (1 + d_rate / 100))) if curr_price > 0 and d_rate != 0 else 0
                    diff_amt_str = fmt_dual(diff_amt_raw, True) if diff_amt_raw != 0 else "0"
                    d_rate_str = "-" if is_s else fmt_p(d_rate); d_class = "" if is_s else col(d_rate)
                    
                    row += f"<td>{pct:.1f}%</td><td>{ia}</td><td class='{col(i.get('평가손익', 0))}'>{ip}</td><td class='{col(i.get('수익률(%)', 0))}'>{fmt_p(i.get('수익률(%)', 0))}</td><td>{fmt(i.get('수량', '-'))}</td><td>{ibuy}</td><td>{icurr}</td>"
                    if st.session_state.gen_show_change_rate:
                        if is_s or i.get('종목명') == '예수금': row += "<td>-</td>"
                        else: row += f"<td style='padding: 4px; line-height: 1.3;'><div class='{d_class}' style='font-size:13px;'>{diff_amt_str}</div><div class='{d_class}' style='font-size:13px;'>{d_rate_str}</div></td>"
                    row += "</tr>"
                    h3.append(row)
                h3.append("</table>")
                st.markdown("".join(h3), unsafe_allow_html=True)
