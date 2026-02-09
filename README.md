# Financial State Engine (Spending Tracker)
> A Domain-Driven Design (DDD) approach to personal financial responsibility.

## 🏗️ Architecture
This is a demonstration of modern Backend Engineering principles applied to financial data management. It moves away from "CRUD-style" apps toward a strict **Domain Model** that handles complex credit states and NAFFL data structures.

* **Framework:** FastAPI / Pydantic v2
* **Pattern:** Domain-Driven Design (DDD) / Repository Pattern
* **Infrastructure:** AWS simulation via LocalStack

## 🛠️ Engineering Focus
* **Strict Schema Validation:** Utilizing `Pydantic` and `attrs` to ensure 100% data integrity for financial records.
* **Test-Driven Development:** Engineered to match strict unit testing frameworks with high code coverage.
* **Cloud Native:** Designed for deployment on AWS, utilizing LocalStack for local development of S3 and DynamoDB integrations.

## 🚧 Status
**Active Development:** Designing the core domain logic and credit state transitions.
