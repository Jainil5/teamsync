from langchain_ollama import ChatOllama

llm = ChatOllama(
    model="gpt-oss:20b-cloud",
    temperature=0,
)

def caption_file_content(document_text):
    messages = [
        (
            "system",
            """You are an enterprise document captioning assistant.

        Task:
        Given a document content string, generate a JSON object with EXACT keys:
        - title (string)
        - caption (string)
        - keywords (array of lowercase strings)

        Rules:
        1) Output ONLY valid JSON. No markdown, no explanations.
        2) Caption must be concise (1-2 lines).
        3) Keywords must be useful for search and include:
        - document type (resume / research paper / policy / dataset / invoice / contract / etc.)
        - key entities (person names, company name, tool names, technologies, project name)
        - important terms/skills
        4) keywords must be lowercase, deduplicated, max 25.
        5) If exact details are missing, make best reasonable guess using the content.
        """,
            ),

            ("human", """DOCUMENT CONTENT:
        John David
        Software Developer

        Summary:
        Backend developer with 3.5 years of experience building scalable APIs.
        Skills: Python, Django, FastAPI, PostgreSQL, Redis, AWS.
        Experience: ABC Tech (2021-2024)
        """),
            ("ai", """{
        "title": "Resume - John David",
        "caption": "Resume of John David, a Software Developer specializing in backend development and scalable APIs using Python (Django/FastAPI), PostgreSQL, Redis, and AWS.",
        "keywords": ["resume", "john david", "software developer", "backend developer", "python", "django", "fastapi", "postgresql", "redis", "aws", "scalable apis", "abc tech"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        Riya Patel
        Human Resources Executive

        Summary:
        2 years experience in recruitment, onboarding, payroll coordination and employee engagement.
        Tools: Zoho People, Excel.
        """),
            ("ai", """{
        "title": "Resume - Riya Patel",
        "caption": "Resume of Riya Patel, an HR Executive with experience in recruitment, onboarding, payroll coordination, and employee engagement using tools like Zoho People and Excel.",
        "keywords": ["resume", "riya patel", "hr", "hr executive", "recruitment", "onboarding", "payroll", "employee engagement", "zoho people", "excel"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        Attention Is All You Need
        Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N. Gomez, Lukasz Kaiser, Illia Polosukhin

        Abstract:
        We propose a new simple network architecture, the Transformer, based solely on attention mechanisms.
        Key terms: self-attention, encoder-decoder, multi-head attention, positional encoding.
        """),
            ("ai", """{
        "title": "Research Paper - Attention Is All You Need (Transformers)",
        "caption": "Research paper introducing the Transformer architecture based entirely on attention mechanisms, including self-attention, multi-head attention, encoder-decoder design, and positional encoding.",
        "keywords": ["research paper", "attention is all you need", "transformers", "transformer architecture", "attention mechanism", "self-attention", "multi-head attention", "encoder-decoder", "positional encoding", "nlp", "deep learning"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        TeamSync Leave Policy

        This policy defines Paid Leave, Sick Leave, Casual Leave, Public Holidays,
        leave approval workflow, and leave rules during probation period.
        """),
            ("ai", """{
        "title": "Leave Policy - TeamSync",
        "caption": "TeamSync leave policy document describing paid, sick, and casual leave types, public holidays, approval workflow, and probation period rules.",
        "keywords": ["leave policy", "teamsync", "policy", "hr policy", "paid leave", "sick leave", "casual leave", "public holidays", "leave approval workflow", "probation period"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        Clothing Sales Dataset (CSV)

        Columns:
        date, store_id, product_category, product_name, units_sold, unit_price, revenue, discount

        This dataset is used for sales forecasting and trend analysis.
        """),
            ("ai", """{
        "title": "Dataset - Clothing Sales Data",
        "caption": "Dataset containing clothing sales records with fields like date, store_id, product category/name, units sold, unit price, revenue, and discount for trend analysis and forecasting.",
        "keywords": ["dataset", "clothing sales", "sales data", "csv", "date", "store_id", "product_category", "product_name", "units_sold", "unit_price", "revenue", "discount", "forecasting", "trend analysis"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        Product Requirements Document (PRD)
        Project: TeamSync Chat Platform

        Objective:
        Build an internal chat app with channels, DMs, file sharing, and admin controls.
        Non-functional: scalability, security, audit logs.
        Tech: React, FastAPI, PostgreSQL.
        """),
            ("ai", """{
        "title": "PRD - TeamSync Chat Platform",
        "caption": "PRD for the TeamSync Chat Platform describing objectives, core features (channels, DMs, file sharing), admin controls, and non-functional requirements like scalability and security.",
        "keywords": ["prd", "product requirements", "teamsync", "chat platform", "channels", "direct messages", "file sharing", "admin controls", "audit logs", "scalability", "security", "react", "fastapi", "postgresql"]
        }"""),

            # ---------------- FEW SHOT 7: SRS / Technical Specification ----------------
            ("human", """DOCUMENT CONTENT:
        Software Requirements Specification (SRS)
        Module: Authentication & Authorization

        Requirements:
        - login via email+password
        - forgot password
        - jwt based auth
        - role based access control (rbac)
        - session timeout 30 minutes
        """),
            ("ai", """{
        "title": "SRS - Authentication & Authorization",
        "caption": "Software requirements specification for authentication and authorization covering login, password reset, JWT-based auth, RBAC, and session timeout rules.",
        "keywords": ["srs", "software requirements", "authentication", "authorization", "jwt", "rbac", "role based access control", "login", "forgot password", "session timeout", "security"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        Minutes of Meeting (MoM)
        Date: 12 Jan 2026
        Topic: Sprint Planning - TeamSync Search

        Decisions:
        - implement hybrid search (bm25 + vectors)
        - use qdrant for embeddings
        - deadline: 25 Jan 2026
        """),
            ("ai", """{
        "title": "MoM - Sprint Planning (TeamSync Search)",
        "caption": "Meeting minutes for TeamSync Search sprint planning including decisions on hybrid search (BM25 + vectors), using Qdrant embeddings, and delivery deadline.",
        "keywords": ["mom", "minutes of meeting", "teamsync", "sprint planning", "search", "hybrid search", "bm25", "vector search", "qdrant", "deadline", "jan 2026"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        INVOICE
        Vendor: AWS (Amazon Web Services)
        Invoice Date: 01-Dec-2025
        Service Period: Nov 2025
        Total Amount Due: $428.16
        Services: EC2, S3, CloudWatch
        """),
            ("ai", """{
        "title": "Invoice - AWS Services (Nov 2025)",
        "caption": "Invoice for AWS cloud services covering EC2, S3, and CloudWatch usage for Nov 2025 with total amount due details.",
        "keywords": ["invoice", "billing", "aws", "amazon web services", "ec2", "s3", "cloudwatch", "cloud services", "nov 2025", "cost"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        NON-DISCLOSURE AGREEMENT (NDA)

        This Agreement is made between TeamSync Technologies Pvt Ltd and Rohan Mehta.
        Confidential Information includes business plans, source code, client details.
        Term: 2 years
        """),
            ("ai", """{
        "title": "NDA - TeamSync and Rohan Mehta",
        "caption": "Non-disclosure agreement between TeamSync Technologies Pvt Ltd and Rohan Mehta defining confidential information (source code, business plans, clients) with a 2-year term.",
        "keywords": ["nda", "non disclosure agreement", "teamsync", "contract", "legal", "confidential information", "source code", "client details", "business plans", "term"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        Information Security Policy

        All employees must use 2FA, strong passwords, and company-managed devices.
        Access to production requires VPN and approval.
        Do not store sensitive credentials in plaintext.
        """),
            ("ai", """{
        "title": "Information Security Policy",
        "caption": "Security policy outlining employee security requirements including 2FA, strong passwords, VPN-based production access, approval workflows, and credential handling rules.",
        "keywords": ["security policy", "information security", "2fa", "password policy", "vpn", "production access", "approval workflow", "credentials", "compliance"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        TeamSync Search API Documentation

        Endpoints:
        POST /search
        GET /documents/{id}
        GET /health

        Auth: Bearer token (JWT)
        Response: top_k results with title, snippet, keywords, score
        """),
            ("ai", """{
        "title": "API Documentation - TeamSync Search API",
        "caption": "API documentation for TeamSync Search service including endpoints for searching, document retrieval, health checks, and JWT-based authentication.",
        "keywords": ["api documentation", "teamsync", "search api", "endpoints", "post /search", "get /documents", "health check", "jwt", "bearer token", "authentication", "top_k results"]
        }"""),

            ("human", """DOCUMENT CONTENT:
        New Employee Onboarding Guide - TeamSync

        Steps:
        1. Laptop & email setup
        2. GitHub access request
        3. Slack + Notion access
        4. Dev environment setup
        5. Security awareness training
        """),
            ("ai", """{
        "title": "Onboarding Guide - TeamSync",
        "caption": "TeamSync onboarding guide outlining steps for laptop/email setup, access requests (GitHub, Slack, Notion), development environment setup, and security training.",
        "keywords": ["onboarding", "teamsync", "new employee", "setup", "github access", "slack", "notion", "dev environment", "security training"]
        }"""),

            ("human", f"""DOCUMENT CONTENT:
        {document_text}
        """),
        ]

    ai_msg = llm.invoke(messages)

    return ai_msg.content


# print(caption_file_content("""
# Project Alpha – Sales Analytics System for Adidas
# Project Name: Project Alpha
# Client: Adidas
# Department: Global Sales and Analytics
# Created by: TeamSync Data Intelligence Division
# Date: October 2025
# 1. Project Overview
# Project Alpha is an advanced sales analytics and forecasting system developed for Adidas
# to analyze, visualize, and optimize sales performance across multiple regions and product
# categories.
# The goal of this project is to help Adidas’ business teams make data-driven decisions by
# understanding sales trends, customer preferences, and market dynamics in real time.
# 2. Objectives
# ● To collect and process sales data from all Adidas retail and online channels.
# ● To generate real-time dashboards for product-wise, region-wise, and month-wise
# performance.
# ● To implement machine learning models for sales forecasting and inventory planning.
# ● To identify top-performing products, peak sales periods, and low-performing
# regions.
# ● To enable management to take predictive and strategic actions based on insights.
# 3. Key Features
# 1. Data Integration:
# Connects to multiple data sources such as Shopify, Zoho, and internal sales databases
# """))
