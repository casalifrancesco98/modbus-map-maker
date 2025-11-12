# Design notes

- MVP focuses on a clean schema and predictable outputs.
- Endianness: `INT32R/FLOAT32R` -> `word_order=swapped` convenience.
- Future: direct binary decode helpers, Modbus RTU/TCP live tester, more emitters (C++/C#).
