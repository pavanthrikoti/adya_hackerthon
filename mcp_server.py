
"""
MedInsight AI - Healthcare Analytics MCP Server
Team 82 - Prompt Pirates
"""

import asyncio
import json
from typing import Any, Dict, List, Optional
from datetime import datetime, timedelta
import random
import sqlite3
from pathlib import Path

# MCP Protocol Implementation
class MCPServer:
    def __init__(self):
        self.name = "medinsight-healthcare-analytics"
        self.version = "1.0.0"
        self.tools = [
            {
                "name": "get_patient_data",
                "description": "Retrieve patient data from DrChrono and Practice Fusion",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "patient_id": {"type": "string"},
                        "date_range": {"type": "string", "enum": ["7d", "30d", "90d"]}
                    }
                }
            },
            {
                "name": "analyze_health_trends",
                "description": "Analyze health trends using ThoughtSpot analytics",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "metric": {"type": "string", "enum": ["appointments", "diagnoses", "treatments"]},
                        "timeframe": {"type": "string", "enum": ["daily", "weekly", "monthly"]}
                    }
                }
            },
            {
                "name": "create_dashboard",
                "description": "Generate interactive dashboard using Metabase",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "dashboard_type": {"type": "string", "enum": ["patient", "provider", "facility"]},
                        "filters": {"type": "array", "items": {"type": "string"}}
                    }
                }
            },
            {
                "name": "send_alert",
                "description": "Send notifications via Slack for critical insights",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "priority": {"type": "string", "enum": ["low", "medium", "high", "critical"]}
                    }
                }
            }
        ]
        self.init_mock_database()
    
    def init_mock_database(self):
        """Initialize mock healthcare database"""
        self.db_path = Path("healthcare_data.db")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id TEXT PRIMARY KEY,
                name TEXT,
                age INTEGER,
                condition TEXT,
                last_visit DATE,
                provider TEXT
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS appointments (
                id TEXT PRIMARY KEY,
                patient_id TEXT,
                provider TEXT,
                appointment_date DATE,
                status TEXT,
                diagnosis TEXT
            )
        ''')
        
        # Insert mock data
        mock_patients = [
            ("P001", "John Doe", 45, "Diabetes", "2025-06-10", "Dr. Smith"),
            ("P002", "Jane Wilson", 32, "Hypertension", "2025-06-12", "Dr. Johnson"),
            ("P003", "Bob Miller", 58, "Heart Disease", "2025-06-15", "Dr. Brown"),
            ("P004", "Alice Davis", 29, "Asthma", "2025-06-16", "Dr. Wilson"),
            ("P005", "Charlie Brown", 67, "Arthritis", "2025-06-17", "Dr. Smith")
        ]
        
        cursor.executemany(
            "INSERT OR REPLACE INTO patients VALUES (?, ?, ?, ?, ?, ?)",
            mock_patients
        )
        
        mock_appointments = [
            ("A001", "P001", "Dr. Smith", "2025-06-20", "scheduled", "Diabetes checkup"),
            ("A002", "P002", "Dr. Johnson", "2025-06-21", "completed", "BP monitoring"),
            ("A003", "P003", "Dr. Brown", "2025-06-22", "scheduled", "Cardiology consult"),
            ("A004", "P004", "Dr. Wilson", "2025-06-23", "cancelled", "Asthma review"),
            ("A005", "P005", "Dr. Smith", "2025-06-24", "scheduled", "Joint pain assessment")
        ]
        
        cursor.executemany(
            "INSERT OR REPLACE INTO appointments VALUES (?, ?, ?, ?, ?, ?)",
            mock_appointments
        )
        
        conn.commit()
        conn.close()

    async def get_patient_data(self, patient_id: str, date_range: str = "30d") -> Dict[str, Any]:
        """DrChrono + Practice Fusion Integration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Get patient info
        cursor.execute("SELECT * FROM patients WHERE id = ?", (patient_id,))
        patient = cursor.fetchone()
        
        if not patient:
            return {"error": "Patient not found"}
        
        # Get appointments
        cursor.execute("""
            SELECT * FROM appointments 
            WHERE patient_id = ? 
            ORDER BY appointment_date DESC
        """, (patient_id,))
        appointments = cursor.fetchall()
        
        conn.close()
        
        return {
            "patient_info": {
                "id": patient[0],
                "name": patient[1],
                "age": patient[2],
                "primary_condition": patient[3],
                "last_visit": patient[4],
                "primary_provider": patient[5]
            },
            "appointments": [
                {
                    "id": apt[0],
                    "provider": apt[2],
                    "date": apt[3],
                    "status": apt[4],
                    "diagnosis": apt[5]
                } for apt in appointments
            ],
            "data_sources": ["DrChrono EHR", "Practice Fusion EMR"],
            "retrieved_at": datetime.now().isoformat()
        }

    async def analyze_health_trends(self, metric: str = "appointments", timeframe: str = "weekly") -> Dict[str, Any]:
        """ThoughtSpot Analytics Integration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if metric == "appointments":
            cursor.execute("""
                SELECT 
                    DATE(appointment_date) as date,
                    COUNT(*) as count,
                    status
                FROM appointments 
                GROUP BY DATE(appointment_date), status
                ORDER BY date DESC
            """)
            data = cursor.fetchall()
            
            trends = {
                "metric": "appointment_trends",
                "timeframe": timeframe,
                "data": [
                    {"date": row[0], "count": row[1], "status": row[2]}
                    for row in data
                ],
                "insights": [
                    "25% increase in appointments this week",
                    "Diabetes patients showing 40% better compliance",
                    "Peak appointment times: 10-11 AM, 2-3 PM"
                ]
            }
        
        elif metric == "diagnoses":
            cursor.execute("""
                SELECT 
                    diagnosis,
                    COUNT(*) as frequency
                FROM appointments 
                WHERE diagnosis IS NOT NULL
                GROUP BY diagnosis
                ORDER BY frequency DESC
            """)
            data = cursor.fetchall()
            
            trends = {
                "metric": "diagnosis_patterns",
                "timeframe": timeframe,
                "data": [
                    {"diagnosis": row[0], "frequency": row[1]}
                    for row in data
                ],
                "insights": [
                    "Diabetes checkups are 35% of all appointments",
                    "Seasonal increase in respiratory conditions",
                    "Preventive care appointments up 20%"
                ]
            }
        
        conn.close()
        
        trends.update({
            "analytics_engine": "ThoughtSpot",
            "generated_at": datetime.now().isoformat(),
            "confidence_score": 0.85
        })
        
        return trends

    async def create_dashboard(self, dashboard_type: str = "facility", filters: List[str] = None) -> Dict[str, Any]:
        """Metabase Dashboard Integration"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if dashboard_type == "facility":
            # Facility overview dashboard
            cursor.execute("SELECT COUNT(*) FROM patients")
            total_patients = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM appointments WHERE status = 'scheduled'")
            upcoming_appointments = cursor.fetchone()[0]
            
            cursor.execute("""
                SELECT provider, COUNT(*) as patient_count 
                FROM patients 
                GROUP BY provider
            """)
            provider_data = cursor.fetchall()
            
            dashboard = {
                "dashboard_id": f"facility_overview_{datetime.now().strftime('%Y%m%d')}",
                "type": "facility",
                "widgets": [
                    {
                        "title": "Total Active Patients",
                        "value": total_patients,
                        "type": "metric",
                        "trend": "+12% from last month"
                    },
                    {
                        "title": "Upcoming Appointments",
                        "value": upcoming_appointments,
                        "type": "metric",
                        "trend": "+5% from last week"
                    },
                    {
                        "title": "Provider Patient Distribution",
                        "data": [{"provider": p[0], "patients": p[1]} for p in provider_data],
                        "type": "chart",
                        "chart_type": "bar"
                    },
                    {
                        "title": "Appointment Status Breakdown",
                        "data": [
                            {"status": "Scheduled", "count": 3},
                            {"status": "Completed", "count": 1},
                            {"status": "Cancelled", "count": 1}
                        ],
                        "type": "chart",
                        "chart_type": "pie"
                    }
                ]
            }
        
        conn.close()
        
        dashboard.update({
            "dashboard_engine": "Metabase",
            "created_at": datetime.now().isoformat(),
            "auto_refresh": "5min",
            "shareable_url": f"https://metabase.medinsight.ai/dashboard/{dashboard['dashboard_id']}"
        })
        
        return dashboard

    async def send_alert(self, message: str, priority: str = "medium") -> Dict[str, Any]:
        """Slack Integration for Notifications"""
        alert_data = {
            "alert_id": f"alert_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            "message": message,
            "priority": priority,
            "timestamp": datetime.now().isoformat(),
            "channel": "#healthcare-alerts" if priority in ["high", "critical"] else "#general-updates",
            "status": "sent",
            "platform": "Slack"
        }
        
        # Simulate Slack webhook
        if priority == "critical":
            alert_data["mentions"] = ["@channel", "@dr-smith", "@nurse-manager"]
        elif priority == "high":
            alert_data["mentions"] = ["@on-call-physician"]
        
        # Add contextual actions
        alert_data["actions"] = [
            {"text": "View Dashboard", "url": "https://medinsight.ai/dashboard"},
            {"text": "Acknowledge", "action": "acknowledge"},
            {"text": "Escalate", "action": "escalate"}
        ]
        
        return alert_data

    async def handle_request(self, method: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Main request handler"""
        try:
            if method == "get_patient_data":
                return await self.get_patient_data(
                    params.get("patient_id", "P001"),
                    params.get("date_range", "30d")
                )
            elif method == "analyze_health_trends":
                return await self.analyze_health_trends(
                    params.get("metric", "appointments"),
                    params.get("timeframe", "weekly")
                )
            elif method == "create_dashboard":
                return await self.create_dashboard(
                    params.get("dashboard_type", "facility"),
                    params.get("filters", [])
                )
            elif method == "send_alert":
                return await self.send_alert(
                    params.get("message", "System notification"),
                    params.get("priority", "medium")
                )
            else:
                return {"error": f"Unknown method: {method}"}
        except Exception as e:
            return {"error": f"Error executing {method}: {str(e)}"}

# Example usage and testing
async def main():
    server = MCPServer()
    
    print("🏥 MedInsight AI - Healthcare Analytics Hub")
    print("=" * 50)
    
    # Test patient data retrieval
    print("\n1. Getting Patient Data (DrChrono + Practice Fusion)...")
    patient_data = await server.handle_request("get_patient_data", {"patient_id": "P001"})
    print(json.dumps(patient_data, indent=2))
    
    # Test analytics
    print("\n2. Analyzing Health Trends (ThoughtSpot)...")
    trends = await server.handle_request("analyze_health_trends", {"metric": "appointments"})
    print(json.dumps(trends, indent=2))
    
    # Test dashboard creation
    print("\n3. Creating Dashboard (Metabase)...")
    dashboard = await server.handle_request("create_dashboard", {"dashboard_type": "facility"})
    print(json.dumps(dashboard, indent=2))
    
    # Test alert system
    print("\n4. Sending Alert (Slack)...")
    alert = await server.handle_request("send_alert", {
        "message": "Critical: Patient P003 missed cardiology appointment - immediate follow-up required",
        "priority": "critical"
    })
    print(json.dumps(alert, indent=2))

if __name__ == "__main__":
    asyncio.run(main())