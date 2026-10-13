# Choose a view and keep its meaning precise

Use the project's source, configuration and actual runtime evidence. A diagram is a model, not evidence that a behavior was tested.

## C4 architecture views

- **Context:** one software system, people and neighboring software systems. Keep internal modules, database tables and worker threads out of this level.
- **Containers:** runtime applications and data stores within the selected system boundary. A container is not necessarily Docker or an independently distributed installer. Explain what shares a process/package and what executes separately.
- **Components:** responsibilities inside one container, with source locations and relevant libraries. Keep an in-process library inside its owning process; do not draw it as a service merely to fill a box.
- Give each element a type, responsibility and relevant technology. Every relationship is directed and labelled; inter-process relationships name their actual channel/protocol. Dependency direction and payload direction can differ, so explain which a view uses.
- Add a curated source map or interface catalog when full method/class graphs would obscure the architecture.

## Data-flow view

Show entities, transformations and stores, with arrows naming data: audio samples, documents, model files, query text, records or results. Keep start/stop/cancel signals in a control/sequence/state view. Explain formats and boundaries only where they matter. Distinguish transient buffers from persisted files and rows, and independent side effects from atomic transactions. Optional remote paths must show which payload crosses them and when.

## Runtime sequence

Use participants, lifelines, messages and returns. Time flows downward; parallel operands do not imply cross-operand order. Explain asynchronous signals/work and synchronous calls in the key. Use `opt`, `alt` and `par` only where the actual scenario supports them. Requests, retries, cancellation, fallback and validation belong to the components that implement them.

Scheduling a callback, returning success, sending a network request or injecting input is not necessarily evidence of receiver acceptance or durable storage. Show acknowledgements only where the implementation provides them. Separate the normal scenario from failure paths if one drawing becomes dense.

## State and exception view

Use actual states, not a mixture of state values, events, flags and queued work. Label transitions with events/guards and describe recovery side effects. Explain whether cancel suppresses future output, waits for tasks to drain, or rolls back existing side effects; those are different contracts.

## Documentation and evidence

An architecture explanation can cover goals/constraints, context, building blocks, interfaces, runtime, deployment, decisions and quality tradeoffs. Tailor the depth; do not create every section or diagram automatically. Keep source/version/date references and observed results separate from intended behavior. Failure handling should describe the actual distinctions, such as missing results versus returned empty results, rather than a reassuring generalization.

Primary guidance:

- [C4 notation](https://c4model.com/diagrams/notation) and [review checklist](https://c4model.com/diagrams/checklist).
- [arc42 overview](https://arc42.org/overview/) and [runtime scenarios](https://docs.arc42.org/section-6/).
- [OMG UML 2.5.1](https://www.omg.org/spec/UML/2.5.1/About-UML), for selected sequence/state conventions.
- [ISO/IEC/IEEE 42010:2022 public abstract](https://www.iso.org/standard/74393.html), for architecture-description viewpoints; using these ideas is not a conformance audit.
- [Diátaxis](https://diataxis.fr/), for explanation/reference/how-to distinctions.
