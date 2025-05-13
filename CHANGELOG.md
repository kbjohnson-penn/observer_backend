# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/). It diverges in the following ways:

- Release titles do not link to the commits within the release
- This project only strictly adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html) for bug fix releases.

## [2.0.0] - 2025-05-13

### Added

- API versioning with v1 routes
- Azure Storage integration for file management
- Penn Personalized Care encounter source support
- Comprehensive mock data generation via management commands
- Docker containerization support

### Changed

- Major file restructuring for improved organization
- Significant database schema migrations and refactoring
- Enhanced API structure with public and private endpoints
- Simplified encounter models into a unified structure

### Removed

- Neo4j integration (simplified architecture)

## [1.2.0] - 2024-03-20

### Added

- Integrated Neo4j database
- Created Nodes and Edges when data added to relational database

## [1.1.0] - 2024-03-14

### Changed

- Expanded patient and provider API view
- Added patient and provider satisfaction scores to the Encounter API
- Changed API root view to ReadOnly

## [1.0.0] - 2024-03-13

### Added

- New database models to include Patient, Provider and Datapaths tables
- APIs
  - /api/patients
  - /api/providers
  - /api/datapaths

### Changed

- APIs
  - /api/encounters
  - /api/departments

### Removed

- APIs
  - /api/media_choices

## [0.1.0] - 2024-02-19

### Added

- APIs
  - /api/encounters
  - /api/departments
  - /api/media_choices
