.. KMDS Data Helper documentation master file

Welcome to KMDS Data Helper's documentation!
============================================

KMDS Data Helper is a specialized tool for auditing and optimizing data science notebooks using LLM-powered personas.

.. toctree::
   :maxdepth: 2
   :caption: Core Documentation

   trace_flow
   personas
   build_instructions

Project Execution Flow
======================

The system follows a specific execution pipeline to analyze notebooks. For a deep dive into the internal logic, state management, and LLM orchestration, please refer to the :doc:`trace_flow`.

Persona Discovery Engine
========================

The tool dynamically discovers "expert" personas from the YAML files stored in your workspace. 

.. note::
   **Crucial Naming Rule:** 
   Files must use ``snake_case`` (e.g., ``modeling_ds.yaml``). The engine automatically converts these to **Title Case** with spaces (e.g., ``Modeling Ds``) for API communication and testing.

To learn more about adding experts or fixing discovery errors, see the :doc:`personas` guide.

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
