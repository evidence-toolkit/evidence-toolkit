# Example Project Plan

This is a template for creating project plans that the `/plan` command can parse to generate phase-specific commands and agents.

## Frontend Setup

Create a modern React application with proper tooling and configuration.

**Goals:**
- Initialize React project with Vite
- Configure TypeScript and ESLint
- Set up Tailwind CSS for styling
- Create basic project structure

**Technologies:**
- React 18
- Vite
- TypeScript
- Tailwind CSS

## Backend API

Build a REST API server with authentication and database integration.

**Goals:**
- Set up Express.js server
- Implement JWT authentication
- Create user CRUD operations
- Connect to PostgreSQL database

**Technologies:**
- Node.js
- Express.js
- PostgreSQL
- JWT tokens

## Database Schema

Design and implement the database schema with proper relationships.

**Goals:**
- Create user tables
- Set up product catalog
- Implement order relationships
- Add indexes for performance

**Technologies:**
- PostgreSQL
- Database migrations
- SQL schemas

## Testing & Quality

Implement comprehensive testing and code quality checks.

**Goals:**
- Unit tests for components
- API integration tests
- E2E testing setup
- Code coverage reporting

**Technologies:**
- Jest
- React Testing Library
- Playwright
- ESLint/Prettier

## Deployment

Deploy the application to production with CI/CD pipeline.

**Goals:**
- Docker containerization
- AWS deployment setup
- CI/CD pipeline configuration
- Environment management

**Technologies:**
- Docker
- AWS (ECS/RDS)
- GitHub Actions
- Environment variables

---

## How to Use This Template

1. **Customize the phases** - Replace with your project's specific phases
2. **Update technologies** - List the actual tech stack you'll use
3. **Modify goals** - Define what each phase should accomplish
4. **Run `/plan`** - The planner will generate phase commands automatically

## Expected Output

After running `/plan` with this template, you'll get commands like:
- `/phase-frontend-setup`
- `/phase-backend-api`
- `/phase-database-schema`
- `/phase-testing-quality`
- `/phase-deployment`

Each command will have a specialized agent that knows how to implement that specific phase using the mentioned technologies.