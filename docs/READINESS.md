# Current readiness: BLOCKED

The current checkout cannot run the complete active box. These are repository
prerequisites, not missing host Node/.NET installations.

| Component | Recorded index SHA | Actual contents / blocker |
| --- | --- | --- |
| frontend/team-squared-app | e01a3475b92fe55808006bf91a470fe97eb2b4ef | README only; no Dockerfile or Makefile. Prompt 2 changes exist in the sibling checkout, not this pin. |
| backend/goalstats-user-service | 70c77c692993fc18e9f484bf22266a15288c0541 | README only; no application, Dockerfile, Makefile, migrations, or test contract. Published HEAD was also this commit when checked. |
| backend/team-squared-service | 47ed7cb27c1a00bf6a4b784276f86182ca3c6d05 | REFERENCE ONLY; never substitute this template for the active backend. |
| frontend/RoadToTheFinal | 4c77197e209292f70ae788e6d4539bb89189e963 | REFERENCE ONLY; excluded from active operations. |

The parent HEAD contains only README.md. Its .gitmodules and four gitlinks are
staged additions, not committed parent pins. No commit, staging, pointer update,
or publication is performed by this implementation.

## Required before certification

1. Publish an app commit containing the Prompt 2 Dockerfile/Make/test contract.
2. Implement and publish the ACTIVE goalstats-user-service in its own repository.
   Supply its actual LOCAL/DEV Dockerfile targets, container port, dependencies,
   runtime variables, readiness/health endpoints, representative GET, migration
   mechanism (or explicitly no migrations), and normal containerized test command.
3. Deliberately pin those published commits in the parent and commit .gitmodules
   and gitlinks. This is maintainer work, never an automatic setup operation.
4. Complete the active backend entries in config/components.tsv and both Compose
   files using that verified contract. Allocate box-owned ports and persistent
   database volumes at that point. Do not guess EF paths or activate the template.
5. Run the documented LOCAL/DEV, persistence, delegation, smoke, standalone-child,
   and clean-clone checks against those real pinned implementations.

The frontend Compose entries reuse the known Prompt 2 contract. They are an
incomplete composition until the active backend is supplied. Public commands guard
against accidentally certifying a frontend-only stack as the complete box.

The app scaffold also has no browser API client yet. A future successful Node
request from the frontend container to a service proves network connectivity, not
an implemented browser-to-backend feature. Full browser integration cannot be
certified without that application behavior.
