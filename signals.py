from technical_indicators import safe_pos


def get_tech_signal(
    close, chgPct, amp, volume_ok,
    k, d, prev_k, prev_d,
    bb_pct,
    bias6, bias18, bias50,
    bias6_min, bias6_max,
    bias18_min, bias18_max,
    bias50_min, bias50_max,
    ma18, prev_ma18, prev_close,
):
    reasons = []

    kd_gold_cross = prev_k <= prev_d and k > d
    kd_dead_cross = prev_k >= prev_d and k < d

    _ma18_break = (
        ma18 is not None and prev_ma18 is not None
        and prev_close <= prev_ma18 and close > ma18
    )

    bias6_pos = safe_pos(bias6, bias6_min, bias6_max)
    bias18_pos = safe_pos(bias18, bias18_min, bias18_max)
    bias50_pos = safe_pos(bias50, bias50_min, bias50_max)

    kd_score = 0
    if kd_gold_cross and k < 35:
        kd_score = 2
        reasons.append('KD低檔黃金交叉')
    elif kd_gold_cross:
        kd_score = 1
        reasons.append('KD黃金交叉')
    elif kd_dead_cross and k > 75:
        kd_score = -2
        reasons.append('KD高檔死亡交叉')
    elif kd_dead_cross:
        kd_score = -1
        reasons.append('KD死亡交叉')

    vol_price_score = 0
    if chgPct > 0 and volume_ok:
        vol_price_score = 2
        reasons.append('價漲量增')
    elif chgPct > 0 and not volume_ok:
        vol_price_score = 1
        reasons.append('上漲但量能普通')
    elif chgPct < 0 and volume_ok:
        vol_price_score = -2
        reasons.append('價跌量增')
    elif chgPct < 0:
        vol_price_score = -1
        reasons.append('股價走弱')

    bb_score = 0
    if bb_pct is not None:
        if bb_pct < 20:
            bb_score = 1
            reasons.append('接近布林下緣')
        elif bb_pct > 95:
            bb_score = -1
            reasons.append('接近布林上緣過熱')
        elif bb_pct > 80:
            bb_score = -0.5
            reasons.append('位於布林高檔區')

    bias_score = 0
    if bias6_pos is not None:
        if bias6_pos < 0.2:
            bias_score += 1
            reasons.append('Bias6接近90日低點')
        elif bias6_pos > 0.8:
            bias_score -= 1
            reasons.append('Bias6接近90日高點')

    if bias18_pos is not None:
        if bias18_pos < 0.2:
            bias_score += 1
            reasons.append('Bias18接近90日低點')
        elif bias18_pos > 0.8:
            bias_score -= 1
            reasons.append('Bias18接近90日高點')

    if bias50_pos is not None:
        if bias50_pos < 0.2:
            bias_score += 0.5
            reasons.append('Bias50偏低')
        elif bias50_pos > 0.8:
            bias_score -= 0.5
            reasons.append('Bias50偏高')

    trend_score = 0
    if ma18 is not None and close > ma18:
        trend_score += 1
        reasons.append('股價站上月線')
    if bias18 is not None and bias18 > 0:
        trend_score += 0.5
    if bias50 is not None and bias50 > 0:
        trend_score += 0.5

    total_score = kd_score + vol_price_score + bb_score + bias_score + trend_score

    if total_score >= 3:
        signal_result = '買進訊號'
    elif total_score <= -3:
        signal_result = '賣出訊號'
    else:
        signal_result = '觀望訊號'

    if signal_result == '買進訊號':
        if (bias6_pos is not None and bias6_pos > 0.9) or (bb_pct is not None and bb_pct > 95):
            strategy = '觀察'
            reason = '雖然技術面轉強，但短線過熱，不宜追價。'
        else:
            strategy = '買入'
            reason = '技術指標同步轉強，適合偏多操作。'
    elif signal_result == '賣出訊號':
        if kd_dead_cross and k > 75:
            strategy = '出貨'
            reason = '高檔轉弱且賣壓出現，應優先出貨。'
        else:
            strategy = '減碼'
            reason = '技術面轉弱，但中期趨勢未完全破壞，先減碼控風險。'
    else:
        if amp < 2 and not volume_ok:
            strategy = '整理'
            reason = '量縮且波動不大，屬整理格局。'
        else:
            strategy = '觀察'
            reason = '技術面方向不明，先觀察等待確認。'

    if signal_result == '買進訊號' and strategy != '買入':
        reason = f'雖然出現買進訊號，但因短線過熱或追價風險偏高，所以策略改為{strategy}。'
    if signal_result == '賣出訊號' and strategy != '出貨':
        reason = f'雖然出現賣出訊號，但中期趨勢未完全破壞，所以策略先採{strategy}。'

    return {
        'signal_result': signal_result,
        'strategy': strategy,
        'reason': reason,
        'signal_text': ' / '.join(reasons) if reasons else '觀望',
    }
