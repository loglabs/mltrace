# Software design doc

## Document Outline

- Introduction
- System Overview
- Design Considerations
  - Assumptions and Dependencies
  - General Constraints
  - Goals and Guidelines
  - Development Methods
- System Architecture
  - component-1 name or description
  - component-2 name or description
  - ...
- Detailed System Design
  - module-1 name or description
  - module-2 name or description
  - ...

## Document Description

Here is the description of the contents (by section and subsection) of the proposed template for software design specifications:

### Introduction

The purpose of this document is to lay out the tech specs for the first version of the debugger. It is intended to describe the user flow, all the (technical) system requirements, and how these requirements will be implemented.

The intended audience is basically myself, as literally no one else is working on this (FML). To see the related product requirements doc, see `prd.md` in the folder. The last part of this document will contain descriptions of tests for the submodules.

### System Overview

The general purpose of this tool is to be able to print a "trace" of steps in a DAG that produced a specific output for a complex data pipeline. This tool is designed for ML pipelines; however it should work for any pipeline that consists of complex function transformations, where each component of the pipeline might be updated or replaced at a different cadence.

# 2.Design Considerations

This section describes many of the issues which need to be addressed or resolved before attempting to devise a complete design solution.

## Assumptions and Dependencies

We are making the following assumptions:

- python-based API

We may reconsider the pipeline concept, as the output of a DAG may come from different pipelines.

## General Constraints

- retrieval of `backtrace` steps should be relatively fast
- after components of the pipeline are registered, you should not have to modify those components much more
- people should be able to register their own types of components
- (TODO: @shreyashankar) possibly require certain types of components to be registered in a specific pipeline

## Goals and Guidelines

- UX over efficiency
- calling `bt` is similar to doing so in a debugger (ex: `gdb`)
- DAG specification of components in an ML pipeline is similar to Airflow's UX
- nontechnical people should be able to print a backtrace corresponding to a specific `output_id`

## Development Methods

We will be using the following tools / technologies:

- Python classes to represent components
- Python API for creating and registering new components
- Postgres tables to represent the entities and relations between them
- (undecided technology) to query the Postgres table to show the backtrace

# Architectural Strategies

For this version of the product, we stick to Python for ease and because most production ML systems have significant parts implemented in Python. 

It is an open question whether to use Django or not. One one hand we can write all the abstractions in pure Python; on the other hand we could probably build this on top of MLFlow. Since this is a fairly simple tool, it makes sense to make it abstract and generalizable to different production pipelines, as not all production piplelines use MLFlow for example.

<!-- Describe any design decisions and/or strategies that affect the overall organization of the system and its higher-level structures. These strategies should provide insight into the key abstractions and mechanisms used in the system architecture. Describe the reasoning employed for each decision and/or strategy (possibly referring to previously stated design goals and principles) and how any design goals or priorities were balanced or traded-off. Such decisions might concern (but are not limited to) things like the following:

- Use of a particular type of product (programming language, database, library, etc. ...)
- Reuse of existing software components to implement various parts/features of the system
- Future plans for extending or enhancing the software
- User interface paradigms (or system input and output models)
- Hardware and/or software interface paradigms
- Error detection and recovery
- Memory management policies
- External databases and/or data storage management and persistence
- Distributed data or control over a network
- Generalized approaches to control
- Concurrency and synchronization
- Communication mechanisms
- Management of other resources

Each significant strategy employed should probably be discussed in its own subsection, or (if it is complex enough) in a separate design document (with an appropriate reference here of course). Make sure that when describing a design decision that you also discuss any other significant alternatives that were considered, and your reasons for rejecting them (as well as your reasons for accepting the alternative you finally chose). Sometimes it may be most effective to employ the &quot;pattern format&quot; for describing a strategy. -->

# System Architecture

At a high level, the system is an abstraction to track runs of various components in a production pipeline and print a trace for any specified output.

An ER diagram is as follows:

![](./er.png)

The entities are:

- component
- component run
- pipeline run

And the relations are:

- component < exec > component run
- component < dependency > component
- pipeline run < consists of > component run

Each of these will be discussed in further detail in the "subsystem architecture" sections.


<!-- 
This section should provide a high-level overview of how the functionality and responsibilities of the system were partitioned and then assigned to subsystems or components. Don&#39;t go into too much detail about the individual components themselves (there is a subsequent section for detailed component descriptions). The main purpose here is to gain a general understanding of how and why the system was decomposed, and how the individual parts work together to provide the desired functionality.

At the top-most level, describe the major responsibilities that the software must undertake and the various roles that the system (or portions of the system) must play. Describe how the system was broken down into its components/subsystems (identifying each top-level component/subsystem and the roles/responsibilities assigned to it). Describe how the higher-level components collaborate with each other in order to achieve the required results. Don&#39;t forget to provide some sort of rationale for choosing this particular decomposition of the system (perhaps discussing other proposed decompositions and why they were rejected). Feel free to make use of design patterns, either in describing parts of the architecture (in pattern format), or for referring to elements of the architecture that employ them.

If there are any diagrams, models, flowcharts, documented scenarios or use-cases of the system behavior and/or structure, they may be included here (unless you feel they are complex enough to merit being placed in the Detailed System Design section). Diagrams that describe a particular component or subsystem should be included within the particular subsection that describes that component or subsystem.

Note:

This section (and its subsections) really applies only to newly developed (or yet-to-be developed) portions of the system. If there are parts of the system that already existed before this development effort began, then you only need to describe the pre-existing parts that the new parts of the system depend upon, and only in enough detail sufficient to describe the relationships and interactions between the old parts and the new parts. Pre-existing parts that are modified or enhanced need to be described only to the extent that is necessary for the reader to gain a sufficient understanding of the nature of the changes that were made. -->

## Subsystem Architecture

TLDR see the ER diagram.

<!-- If a particular component is one which merits a more detailed discussion than what was presented in the System Architecture section, provide that more detailed discussion in a subsection of the System Architecture section (or it may even be more appropriate to describe the component in its own design document). If necessary, describe how the component was further divided into subcomponents, and the relationships and interactions between the subcomponents (similar to what was done for top-level components in the System Architecture section).

If any subcomponents are also deemed to merit further discussion, then describe them in a separate subsection of this section (and in a similar fashion). Proceed to go into as many levels/subsections of discussion as needed in order for the reader to gain a high-level understanding of the entire system or subsystem (but remember to leave the gory details for the Detailed System Design section).

If this component is very large and/or complex, you may want to consider documenting its design in a separate document and simply including a reference to it in this section. If this is the option you choose, the design document for this component should have an organizational format that is very similar (if not identical to) this document. -->

# Detailed System Design

<!-- Most components described in the System Architecture section will require a more detailed discussion. Other lower-level components and subcomponents may need to be described as well. Each subsection of this section will refer to or contain a detailed description of a system software component. The discussion provided should cover the following software component attributes: -->

In this section, we discuss how a user would interact with the system and leverage it to `backtrace` an output. First, we talk about a high level overview of the pipeline a user might have, and then how the user would interact with our system.

## Overview of a generic applied ML pipeline

Consider a pipeline that takes in raw data and produces an output for a specific prediction task. For example, imagine inputs of raw sensor data and ouptuts of whether the machine will experience downtime in the next month. There are several stages in this pipeline, such as:

1. ETL
2. Feature generation
3. Train set selection
4. Model training
5. Model inference

Each of these stages can have multiple components, which will differ based on application and/or company. In each of these stages also, there may be different I/O. Thus, we will need a general-purpose abstraction that allows users to get an end-to-end trace based on various function transforms.

## User interaction with system

Suppose a user has a pipeline of components (maybe a few of those components are ML-based) and versions each of those components. Every output has gone through a series of runs of each of these components. For a simple example, imagine the pipeline is as follows:

```
def clean(raw_data_path):
    ...
    return clean_data

def featurize(clean_data_path):
    features_dict = ...
    return pd.DataFrame(features_dict)

def inference(features_path, model_id):
    model = load_model(model_id)
    features = load_features(features_path)
    return models(features)

def serve(path):
    ...
    return output
```

The output of `serve` is presented to the entity interacting with the predictions. First, these outputs need to be id'ed. Either the user can specify the id, or our system will generate an id for the output. To do so, we would like for the user to register the serving component similar to as follows:

```
serve_component = create_or_retrieve_component('serve')
serve_component.set_description('some description')
serve_component.set_owner('@kimkardashian')

@register(component=serve_component, input_path=path, output_path=None, git_hash=None)
def serve(path):
    ...
    log(output_id, component=serve_component)
    return output
```

Behind the scenes, our system would log the output id to a database with pointers to dynamic information generated by the `@register`.

