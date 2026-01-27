"""Combination alert system - multiple conditions."""
from typing import Dict, Optional, List


class CombinationAlerts:
    """Evaluate alerts with multiple conditions."""
    
    @staticmethod
    def mc_and_volume_spike(
        current_mc: float,
        mc_target: float,
        volume_24h: float,
        avg_volume: float,
        volume_multiplier: float = 3.0
    ) -> Optional[Dict]:
        """
        Alert if MC target hit AND volume spike detected.
        
        Args:
            current_mc: Current market cap
            mc_target: MC target threshold
            volume_24h: Current 24h volume
            avg_volume: Average 24h volume
            volume_multiplier: Volume spike threshold (default 3x)
        
        Returns:
            Alert details if both conditions met
        """
        mc_met = current_mc >= mc_target
        volume_spike = volume_24h >= (avg_volume * volume_multiplier) if avg_volume > 0 else False
        
        if mc_met and volume_spike:
            return {
                "type": "combo_mc_volume",
                "mc": current_mc,
                "mc_target": mc_target,
                "volume": volume_24h,
                "avg_volume": avg_volume,
                "spike_multiplier": volume_24h / avg_volume if avg_volume > 0 else 0
            }
        
        return None
    
    @staticmethod
    def pct_and_volume(
        current_mc: float,
        start_mc: float,
        pct_target: float,
        volume_24h: float,
        min_volume: float
    ) -> Optional[Dict]:
        """
        Alert if % change met AND minimum volume threshold met.
        
        Args:
            current_mc: Current market cap
            start_mc: Starting market cap
            pct_target: % change target
            volume_24h: Current 24h volume
            min_volume: Minimum volume threshold
        
        Returns:
            Alert details if both conditions met
        """
        if start_mc == 0:
            return None
        
        pct_change = abs((current_mc - start_mc) / start_mc * 100)
        pct_met = pct_change >= pct_target
        volume_met = volume_24h >= min_volume
        
        if pct_met and volume_met:
            return {
                "type": "combo_pct_volume",
                "pct": pct_change,
                "pct_target": pct_target,
                "volume": volume_24h,
                "min_volume": min_volume,
                "mc": current_mc
            }
        
        return None
    
    @staticmethod
    def x_and_liquidity(
        current_mc: float,
        start_mc: float,
        x_target: float,
        liquidity: float,
        min_liquidity: float
    ) -> Optional[Dict]:
        """
        Alert if X multiple hit AND liquidity above threshold.
        
        Args:
            current_mc: Current market cap
            start_mc: Starting market cap
            x_target: X multiple target
            liquidity: Current liquidity
            min_liquidity: Minimum liquidity threshold
        
        Returns:
            Alert details if both conditions met
        """
        if start_mc == 0:
            return None
        
        current_x = current_mc / start_mc
        x_met = current_x >= x_target
        liquidity_met = liquidity >= min_liquidity
        
        if x_met and liquidity_met:
            return {
                "type": "combo_x_liquidity",
                "x": current_x,
                "x_target": x_target,
                "liquidity": liquidity,
                "min_liquidity": min_liquidity,
                "mc": current_mc
            }
        
        return None
    
    @staticmethod
    def triple_combo(
        current_mc: float,
        start_mc: float,
        mc_target: float,
        pct_target: float,
        volume_24h: float,
        min_volume: float
    ) -> Optional[Dict]:
        """
        Alert if MC target AND % change AND volume all met.
        
        Returns:
            Alert details if all three conditions met
        """
        if start_mc == 0:
            return None
        
        mc_met = current_mc >= mc_target
        pct_change = abs((current_mc - start_mc) / start_mc * 100)
        pct_met = pct_change >= pct_target
        volume_met = volume_24h >= min_volume
        
        if mc_met and pct_met and volume_met:
            return {
                "type": "combo_triple",
                "mc": current_mc,
                "mc_target": mc_target,
                "pct": pct_change,
                "pct_target": pct_target,
                "volume": volume_24h,
                "min_volume": min_volume
            }
        
        return None
    
    @staticmethod
    def evaluate_all_combos(
        current_mc: float,
        start_mc: float,
        volume_24h: float,
        liquidity: float,
        avg_volume: float,
        combo_alerts: Dict,
        combo_triggered: Dict
    ) -> List[tuple]:
        """
        Evaluate all configured combination alerts.
        
        Args:
            current_mc: Current market cap
            start_mc: Starting market cap
            volume_24h: Current 24h volume
            liquidity: Current liquidity
            avg_volume: Average volume
            combo_alerts: Dict of configured combo alerts
            combo_triggered: Dict tracking which combos have fired
        
        Returns:
            List of (combo_type, details) tuples for alerts to fire
        """
        results = []
        
        # MC + Volume Spike
        if "mc_volume" in combo_alerts and not combo_triggered.get("mc_volume"):
            config = combo_alerts["mc_volume"]
            result = CombinationAlerts.mc_and_volume_spike(
                current_mc,
                config.get("mc_target"),
                volume_24h,
                avg_volume,
                config.get("volume_multiplier", 3.0)
            )
            if result:
                results.append(("mc_volume", result))
        
        # % + Volume
        if "pct_volume" in combo_alerts and not combo_triggered.get("pct_volume"):
            config = combo_alerts["pct_volume"]
            result = CombinationAlerts.pct_and_volume(
                current_mc,
                start_mc,
                config.get("pct_target"),
                volume_24h,
                config.get("min_volume")
            )
            if result:
                results.append(("pct_volume", result))
        
        # X + Liquidity
        if "x_liquidity" in combo_alerts and not combo_triggered.get("x_liquidity"):
            config = combo_alerts["x_liquidity"]
            result = CombinationAlerts.x_and_liquidity(
                current_mc,
                start_mc,
                config.get("x_target"),
                liquidity,
                config.get("min_liquidity")
            )
            if result:
                results.append(("x_liquidity", result))
        
        # Triple combo
        if "triple" in combo_alerts and not combo_triggered.get("triple"):
            config = combo_alerts["triple"]
            result = CombinationAlerts.triple_combo(
                current_mc,
                start_mc,
                config.get("mc_target"),
                config.get("pct_target"),
                volume_24h,
                config.get("min_volume")
            )
            if result:
                results.append(("triple", result))
        
        return results
