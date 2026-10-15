# Navigating the `workspace` directory

This `workspace` directory contains all of the resources you need (other than gem5 itself) to participate in the gem5 online bootcamp.

## Organization

The `workspace` directory has a sub-directory for each unit of the bootcamp, and each of those directories has sub-directories for each section:

```bash
workspace
    ├── 01-introduction
    │   └── 04-first-config-script
    │       └── ...
    ├── 02-beginning-simulation
    ├── 03-intermediate-features
    ├── 04-a-processors
    ├── 04-b-caches
    ├── 04-c-memory
    ├── 05-advanced-topics
    │   ├── 01-kvm-fast-forwarding
    │   │   └── ...
    │   ├── 02-checkpointing
    │   │   ├── ...
    │   ├── ...
    └── NAVIGATION.md
```

If a particular section of the bootcamp has no resources associated with it, its sub-directory is omitted.

## The `completed` sub-directory

Some of the section directories will contain a sub-directory named `completed`. This sub-directory contains the completed versions of the scripts you were tasked with editing; you should be able to recreate the `completed` version by following the steps on that section's lesson, but if something goes wrong along the way, you can always use the `completed` directory to get the same results.
