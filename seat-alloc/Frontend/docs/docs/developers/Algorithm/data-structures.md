---
sidebar_label: 📁 Data Structures
---
import CodeHeader from '@site/src/components/filetypeheaderstyle';
import MagicBento from '@site/src/components/MagicBento';

<style>{`
  [data-theme='light'] .bento-card {
    border: 1px solid #f97316 !important;
  }
`}</style>

# 📁 Data Structures

The algorithm relies on several core data classes and structures to maintain state and represent the physical environment. These structures are designed for high-performance retrieval during the constraint-solving phase.

---

## 1. Core Classes

### `Seat` (Dataclass)
The fundamental unit of the grid. Every coordinate in the room corresponds to a `Seat` object. This class acts as a descriptor for the physical state of a specific location.

<CodeHeader title="PYTHON">
{`@dataclass
class Seat:
    row: int
    col: int
    batch: Optional[int] = None
    paper_set: Optional[PaperSet] = None
    block: Optional[int] = None
    roll_number: Optional[str] = None
    student_name: str = ""
    is_broken: bool = False
    is_unallocated: bool = False
    color: str = "#E5E7EB"`}
</CodeHeader>

### `PaperSet` (Enum)
A simple toggle for A/B alternation. Using an Enum ensures type safety throughout the allocation engine.

<CodeHeader title="PYTHON">
{`class PaperSet(Enum):
    A = "A"
    B = "B"`}
</CodeHeader>

| Field | Description |
| :--- | :--- |
| `batch` | ID of the student group (1-10+). Used for color coding and column-mapping. |
| `paper_set` | Enum value: `PaperSet.A` or `PaperSet.B`. Determined by the priority logic. |
| `block` | Calculated as `col // block_width`. Used to identify the seating section. |
| `roll_number` | The unique identifier for the student. If real data isn't provided, this is auto-generated based on the batch prefix. |
| `is_broken` | Flag for physically damaged/unavailable seats. The engine skips these during allocation. |
| `is_unallocated` | True if the seat was skipped due to a constraint or if it remains empty after filling. |

---

## 2. Allocation State

During generation, the engine maintains an internal `AllocationState` to track progress and enforce constraints:

- **Seating Plan**: A 2D matrix (`List[List[Seat]]`) representing the classroom grid. It is initialized with default `Seat` objects before the filling logic starts.
- **Batch Queues**: `collections.deque` structures containing the students pending allocation. `deque` is used for O(1) pops from the left, ensuring performance for large student lists.
- **Batch Allocated**: A counter mapping batch IDs to the number of students currently placed. This is used to stop filling once a batch reaches its limit.
- **Broken Seats**: A `set` of `(row, col)` tuples. Using a set allows for O(1) lookup during the main filling loop to instantly skip damaged furniture.

---

## 3. Configuration Models

The `SeatingAlgorithm` constructor accepts configuration dictionaries that define the rules for the session:

- `batch_student_counts`: `Dict[int, int]` - Maps batch IDs to total students allowed.
- `batch_roll_numbers`: `Dict[int, List[str]]` - Maps batches to lists of actual enrollment strings (Real Data Mode).
- `batch_prefixes`: `Dict[int, string]` - Prefixes for templated roll numbers (e.g., `1: "BTCS-2024-"`).
- `batch_labels`: `Dict[int, string]` - Human-readable branch names (e.g., `1: "Computer Science"`).

<a href="./paper-set-priority" style={{ textDecoration: 'none', color: 'inherit' }}>
  <MagicBento glowColor="245, 158, 11" enableStars={false} className="bento-card">
    <div style={{ display: 'flex', alignItems: 'center', gap: '1.2rem' }}>
      <div style={{ background: '#f59e0b', width: '45px', height: '45px', borderRadius: '12px', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.5rem', boxShadow: '0 4px 12px rgba(245, 158, 11, 0.3)' }}>💡</div>
      <div style={{ flex: 1 }}>
        <h4 style={{ margin: 0, color: '#f59e0b' }}>Integrity Tip: <code>batch_labels</code></h4>
        <p style={{ margin: 0, fontSize: '0.9rem', opacity: 0.8 }}>Using labels is critical for the <b>Paper Set Priority Logic</b>, allowing multiple IDs to share the same integrity rules (e.g., CSE-A and CSE-B).</p>
      </div>
      <div style={{ opacity: 0.4, fontSize: '1.5rem' }}>→</div>
    </div>
  </MagicBento>
</a>
