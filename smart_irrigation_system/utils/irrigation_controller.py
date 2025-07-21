import time
import threading
from datetime import datetime, timedelta
import json
import schedule
import logging

class IrrigationController:
    def __init__(self):
        self.is_active = False
        self.auto_mode = True
        self.current_session = None
        self.schedule_jobs = []
        self.settings = {
            'moisture_trigger': 30,  # Trigger irrigation when soil moisture below this %
            'default_duration': 15,  # Default irrigation duration in minutes
            'max_daily_sessions': 5,  # Maximum irrigation sessions per day
            'min_interval_hours': 2,  # Minimum hours between irrigation sessions
            'water_flow_rate': 10,  # Liters per minute
            'pressure_threshold': 2.0,  # Minimum water pressure (bar)
        }
        self.daily_sessions = []
        self.system_health = True
        self.last_irrigation = None
        self.total_water_used_today = 0
        
        # Setup logging
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
        # Start the automation thread
        self.automation_thread = threading.Thread(target=self._automation_loop, daemon=True)
        self.automation_running = True
        self.automation_thread.start()
    
    def start_irrigation(self, duration_minutes=None, manual=True, reason="Manual start"):
        """Start irrigation system"""
        if self.is_active:
            self.logger.warning("Irrigation system is already active")
            return False
        
        # Check system health
        if not self._check_system_health():
            self.logger.error("Cannot start irrigation: System health check failed")
            return False
        
        # Check daily limits
        if len(self.daily_sessions) >= self.settings['max_daily_sessions'] and not manual:
            self.logger.warning("Daily irrigation limit reached")
            return False
        
        # Check minimum interval
        if self.last_irrigation and not manual:
            time_since_last = datetime.now() - self.last_irrigation
            if time_since_last < timedelta(hours=self.settings['min_interval_hours']):
                self.logger.warning("Minimum interval between irrigations not met")
                return False
        
        duration = duration_minutes or self.settings['default_duration']
        
        self.current_session = {
            'start_time': datetime.now(),
            'duration_minutes': duration,
            'manual': manual,
            'reason': reason,
            'water_used': 0,
            'status': 'active'
        }
        
        self.is_active = True
        self.logger.info(f"Irrigation started: {duration} minutes, Reason: {reason}")
        
        # Start irrigation in a separate thread
        irrigation_thread = threading.Thread(
            target=self._run_irrigation_session, 
            args=(duration,), 
            daemon=True
        )
        irrigation_thread.start()
        
        return True
    
    def stop_irrigation(self, reason="Manual stop"):
        """Stop irrigation system"""
        if not self.is_active:
            self.logger.warning("Irrigation system is not active")
            return False
        
        self.is_active = False
        
        if self.current_session:
            self.current_session['end_time'] = datetime.now()
            self.current_session['actual_duration'] = (
                self.current_session['end_time'] - self.current_session['start_time']
            ).total_seconds() / 60
            self.current_session['stop_reason'] = reason
            self.current_session['status'] = 'completed'
            
            # Add to daily sessions
            self.daily_sessions.append(self.current_session.copy())
            self.last_irrigation = self.current_session['end_time']
            
            self.logger.info(f"Irrigation stopped: {reason}")
        
        return True
    
    def _run_irrigation_session(self, duration_minutes):
        """Run irrigation session in background"""
        start_time = time.time()
        end_time = start_time + (duration_minutes * 60)
        
        while time.time() < end_time and self.is_active:
            # Simulate water flow and monitor system
            elapsed_minutes = (time.time() - start_time) / 60
            water_used = elapsed_minutes * self.settings['water_flow_rate']
            
            if self.current_session:
                self.current_session['water_used'] = water_used
                self.total_water_used_today += self.settings['water_flow_rate'] / 60  # per second
            
            # Check system health during irrigation
            if not self._check_system_health():
                self.stop_irrigation("System health check failed")
                break
            
            time.sleep(1)  # Check every second
        
        # Auto-stop when duration is reached
        if self.is_active:
            self.stop_irrigation("Duration completed")
    
    def schedule_irrigation(self, time_str, duration_minutes, days_of_week=None):
        """Schedule irrigation at specific times"""
        if isinstance(time_str, str):
            schedule_time = datetime.strptime(time_str, "%H:%M").time()
        else:
            schedule_time = time_str
        
        def irrigation_job():
            if self.auto_mode:
                self.start_irrigation(
                    duration_minutes=duration_minutes,
                    manual=False,
                    reason=f"Scheduled irrigation at {schedule_time}"
                )
        
        # Schedule the job
        if days_of_week:
            for day in days_of_week:
                getattr(schedule.every(), day.lower()).at(schedule_time.strftime("%H:%M")).do(irrigation_job)
        else:
            schedule.every().day.at(schedule_time.strftime("%H:%M")).do(irrigation_job)
        
        self.schedule_jobs.append({
            'time': schedule_time,
            'duration': duration_minutes,
            'days': days_of_week or ['daily'],
            'created': datetime.now()
        })
        
        self.logger.info(f"Irrigation scheduled for {schedule_time} ({duration_minutes} minutes)")
        return True
    
    def set_auto_settings(self, settings):
        """Update automatic irrigation settings"""
        self.settings.update(settings)
        self.auto_mode = settings.get('auto_enabled', self.auto_mode)
        self.logger.info(f"Auto irrigation settings updated: {settings}")
    
    def _automation_loop(self):
        """Main automation loop"""
        while self.automation_running:
            try:
                # Run scheduled tasks
                schedule.run_pending()
                
                # Check for automatic irrigation triggers
                if self.auto_mode and not self.is_active:
                    self._check_auto_irrigation_triggers()
                
                # Reset daily counters at midnight
                self._reset_daily_counters()
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                self.logger.error(f"Error in automation loop: {e}")
                time.sleep(60)
    
    def _check_auto_irrigation_triggers(self):
        """Check if automatic irrigation should be triggered"""
        try:
            # This would integrate with the IoT sensor data
            # For now, we'll simulate the check
            
            # Check soil moisture (would get from sensor)
            current_moisture = self._get_current_soil_moisture()
            
            if current_moisture < self.settings['moisture_trigger']:
                # Check if we can irrigate (time constraints, daily limits, etc.)
                if self._can_auto_irrigate():
                    self.start_irrigation(
                        duration_minutes=self.settings['default_duration'],
                        manual=False,
                        reason=f"Auto trigger: Soil moisture {current_moisture}% < {self.settings['moisture_trigger']}%"
                    )
                    
        except Exception as e:
            self.logger.error(f"Error checking auto irrigation triggers: {e}")
    
    def _get_current_soil_moisture(self):
        """Get current soil moisture from sensors"""
        # This would integrate with the IoT sensor simulator
        # For now, return a simulated value
        import random
        return random.uniform(20, 80)
    
    def _can_auto_irrigate(self):
        """Check if automatic irrigation is allowed"""
        # Check daily session limit
        if len(self.daily_sessions) >= self.settings['max_daily_sessions']:
            return False
        
        # Check minimum interval
        if self.last_irrigation:
            time_since_last = datetime.now() - self.last_irrigation
            if time_since_last < timedelta(hours=self.settings['min_interval_hours']):
                return False
        
        # Check time of day (avoid irrigation during hot hours)
        current_hour = datetime.now().hour
        if 11 <= current_hour <= 16:  # Avoid 11 AM to 4 PM
            return False
        
        return True
    
    def _check_system_health(self):
        """Check irrigation system health"""
        # Simulate system health checks
        # In real implementation, this would check:
        # - Water pressure
        # - Pump status
        # - Valve status
        # - Flow sensors
        # - Electrical connections
        
        health_checks = {
            'water_pressure': self._check_water_pressure(),
            'pump_status': self._check_pump_status(),
            'valve_status': self._check_valve_status(),
            'flow_sensor': self._check_flow_sensor(),
            'electrical': self._check_electrical_system()
        }
        
        self.system_health = all(health_checks.values())
        
        if not self.system_health:
            failed_components = [k for k, v in health_checks.items() if not v]
            self.logger.error(f"System health check failed: {failed_components}")
        
        return self.system_health
    
    def _check_water_pressure(self):
        """Check water pressure"""
        # Simulate pressure check
        import random
        pressure = random.uniform(1.5, 3.0)
        return pressure >= self.settings['pressure_threshold']
    
    def _check_pump_status(self):
        """Check water pump status"""
        # Simulate pump check
        import random
        return random.random() > 0.05  # 5% chance of pump failure
    
    def _check_valve_status(self):
        """Check irrigation valve status"""
        # Simulate valve check
        import random
        return random.random() > 0.02  # 2% chance of valve failure
    
    def _check_flow_sensor(self):
        """Check water flow sensor"""
        # Simulate flow sensor check
        import random
        return random.random() > 0.03  # 3% chance of sensor failure
    
    def _check_electrical_system(self):
        """Check electrical system"""
        # Simulate electrical system check
        import random
        return random.random() > 0.01  # 1% chance of electrical failure
    
    def _reset_daily_counters(self):
        """Reset daily counters at midnight"""
        now = datetime.now()
        if now.hour == 0 and now.minute == 0:
            self.daily_sessions = []
            self.total_water_used_today = 0
            self.logger.info("Daily counters reset")
    
    def get_status(self):
        """Get current irrigation system status"""
        status = {
            'active': self.is_active,
            'auto_mode': self.auto_mode,
            'system_health': self.system_health,
            'current_session': self.current_session,
            'daily_sessions_count': len(self.daily_sessions),
            'total_water_used_today': self.total_water_used_today,
            'last_irrigation': self.last_irrigation,
            'scheduled_jobs': len(self.schedule_jobs),
            'settings': self.settings
        }
        
        if self.current_session:
            status['start_time'] = self.current_session['start_time']
            status['duration'] = self.current_session['duration_minutes']
            status['water_used'] = self.current_session['water_used']
        
        return status
    
    def get_irrigation_history(self, days=7):
        """Get irrigation history"""
        cutoff_date = datetime.now() - timedelta(days=days)
        
        # Filter sessions within the date range
        filtered_sessions = []
        for session in self.daily_sessions:
            if session['start_time'] >= cutoff_date:
                filtered_sessions.append(session)
        
        return filtered_sessions
    
    def get_water_usage_stats(self):
        """Get water usage statistics"""
        today_usage = sum(session.get('water_used', 0) for session in self.daily_sessions)
        
        stats = {
            'today_usage_liters': today_usage,
            'today_sessions': len(self.daily_sessions),
            'avg_session_duration': sum(session.get('actual_duration', 0) for session in self.daily_sessions) / max(len(self.daily_sessions), 1),
            'efficiency_score': self._calculate_efficiency_score()
        }
        
        return stats
    
    def _calculate_efficiency_score(self):
        """Calculate irrigation efficiency score"""
        # Simple efficiency calculation based on:
        # - Number of automatic vs manual sessions
        # - Water usage per session
        # - System health
        
        if not self.daily_sessions:
            return 100
        
        auto_sessions = sum(1 for session in self.daily_sessions if not session.get('manual', True))
        total_sessions = len(self.daily_sessions)
        
        auto_ratio = auto_sessions / total_sessions if total_sessions > 0 else 0
        health_score = 100 if self.system_health else 50
        
        efficiency = (auto_ratio * 50) + (health_score * 0.5)
        return min(100, max(0, efficiency))
    
    def export_irrigation_data(self, filename=None):
        """Export irrigation data to JSON"""
        if filename is None:
            filename = f"irrigation_data_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        export_data = {
            'settings': self.settings,
            'daily_sessions': self.daily_sessions,
            'schedule_jobs': self.schedule_jobs,
            'system_status': self.get_status(),
            'export_timestamp': datetime.now().isoformat()
        }
        
        # Convert datetime objects to strings for JSON serialization
        def serialize_datetime(obj):
            if isinstance(obj, datetime):
                return obj.isoformat()
            return obj
        
        with open(filename, 'w') as f:
            json.dump(export_data, f, indent=2, default=serialize_datetime)
        
        return filename
    
    def emergency_stop(self):
        """Emergency stop of irrigation system"""
        self.stop_irrigation("Emergency stop")
        self.auto_mode = False
        self.system_health = False
        self.logger.critical("EMERGENCY STOP: Irrigation system halted")
    
    def reset_system(self):
        """Reset irrigation system to default state"""
        self.stop_irrigation("System reset")
        self.daily_sessions = []
        self.total_water_used_today = 0
        self.system_health = True
        self.auto_mode = True
        
        # Clear scheduled jobs
        schedule.clear()
        self.schedule_jobs = []
        
        self.logger.info("Irrigation system reset to default state")
    
    def run_diagnostic(self):
        """Run comprehensive system diagnostic"""
        diagnostic_results = {
            'timestamp': datetime.now(),
            'system_health': self._check_system_health(),
            'water_pressure': self._check_water_pressure(),
            'pump_status': self._check_pump_status(),
            'valve_status': self._check_valve_status(),
            'flow_sensor': self._check_flow_sensor(),
            'electrical': self._check_electrical_system(),
            'settings_valid': self._validate_settings(),
            'schedule_valid': self._validate_schedule()
        }
        
        overall_health = all([
            diagnostic_results['system_health'],
            diagnostic_results['settings_valid'],
            diagnostic_results['schedule_valid']
        ])
        
        diagnostic_results['overall_status'] = 'PASS' if overall_health else 'FAIL'
        
        self.logger.info(f"Diagnostic completed: {diagnostic_results['overall_status']}")
        return diagnostic_results
    
    def _validate_settings(self):
        """Validate irrigation settings"""
        required_settings = ['moisture_trigger', 'default_duration', 'water_flow_rate']
        return all(setting in self.settings for setting in required_settings)
    
    def _validate_schedule(self):
        """Validate scheduled irrigation jobs"""
        # Check if scheduled jobs are valid
        return True  # Simplified validation
    
    def cleanup(self):
        """Cleanup resources when shutting down"""
        self.automation_running = False
        if self.is_active:
            self.stop_irrigation("System shutdown")
        
        if self.automation_thread and self.automation_thread.is_alive():
            self.automation_thread.join(timeout=5)
        
        self.logger.info("Irrigation controller cleanup completed")