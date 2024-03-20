# Changelog

We use for versioning.
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). It diverges in the following ways:

- Release titles do not link to the commits within the release
- This project only strictly adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for bug fix releases.

# [1.2.0] - 2024-03-20

## Added

- Integrated Neo4j database

- Creating Nodes and Edges when data added to relational database

# [1.1.0] - 2024-03-14

## Changed

- Expanded patient and provider API view

- Added patient and provider statisfaction scores to the Encouter API

- Changed API root view to ReadOnly

# [1.0.0] - 2024-03-13

## Added

- New database models to include Patient, Provider and Datapaths tables

- APIs
  - /api/patients
  - /api/providers
  - /api/datapaths

## Changed

- APIs
  - /api/encounters
  - /api/departments

## Removed

- APIs
  - /api/media_choices

# [0.1.0] - 2024-02-19

## Added

- APIs
  - /api/encounters
  - /api/departments
  - /api/media_choices
