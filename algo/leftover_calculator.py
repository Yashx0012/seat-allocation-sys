"""
SeatAlloc v2.0 - Leftover Calculator
Calculates unallocated students after seating plan generation
"""

from typing import Dict, List, Any


class LeftoverCalculator:
    """Calculate leftover students after allocation"""
    
    @staticmethod
    def calculate_leftovers(
        total_seats: int,
        allocated_seats: int,
        batch_totals: Dict[int, int],
        batch_allocated: Dict[int, int],
        broken_seats: int = 0
    ) -> Dict[str, Any]:
        """
        Calculate leftover students and allocation statistics
        
        Args:
            total_seats: Total available seats in room
            allocated_seats: Seats filled with students
            batch_totals: Total students per batch {batch_id: count}
            batch_allocated: Allocated students per batch {batch_id: count}
            broken_seats: Number of broken/unusable seats
            
        Returns:
            Dictionary with detailed leftover analysis
        """
        
        total_students = sum(batch_totals.values())
        available_seats = total_seats - broken_seats
        overall_leftovers = total_students - allocated_seats
        
        batch_leftovers = {}
        for batch_id, total in batch_totals.items():
            allocated = batch_allocated.get(batch_id, 0)
            leftover = total - allocated
            
            batch_leftovers[batch_id] = {
                'batch_id': batch_id,
                'total': total,
                'allocated': allocated,
                'leftover': leftover,
                'allocation_percentage': round((allocated / total * 100) if total > 0 else 0, 2)
            }
        
        return {
            'summary': {
                'total_students': total_students,
                'total_seats': total_seats,
                'broken_seats': broken_seats,
                'available_seats': available_seats,
                'allocated': allocated_seats,
                'overall_leftover': overall_leftovers,
                'capacity_utilization': round((allocated_seats / available_seats * 100) if available_seats > 0 else 0, 2),
                'student_allocation_percentage': round((allocated_seats / total_students * 100) if total_students > 0 else 0, 2),
                'allocation_status': 'complete' if overall_leftovers == 0 else 'incomplete'
            },
            'batch_breakdown': batch_leftovers
        }
    
    @staticmethod
    def get_leftover_report(seating_grid: List[List[Dict]], batch_totals: Dict[int, int]) -> Dict[str, Any]:
        """
        Generate leftover report from seating grid
        
        Args:
            seating_grid: 2D grid of seat data
            batch_totals: Total students per batch
            
        Returns:
            Leftover analysis dictionary
        """
        
        rows = len(seating_grid)
        cols = len(seating_grid[0]) if rows > 0 else 0
        total_seats = rows * cols
        
        # Count allocated and broken seats
        allocated_count = 0
        broken_count = 0
        batch_allocated = {}
        
        for row in seating_grid:
            for seat in row:
                if seat.get('is_broken'):
                    broken_count += 1
                elif not seat.get('is_unallocated'):
                    allocated_count += 1
                    batch_id = seat.get('batch', 1)
                    batch_allocated[batch_id] = batch_allocated.get(batch_id, 0) + 1
        
        return LeftoverCalculator.calculate_leftovers(
            total_seats=total_seats,
            allocated_seats=allocated_count,
            batch_totals=batch_totals,
            batch_allocated=batch_allocated,
            broken_seats=broken_count
        )
    
    @staticmethod
    def format_for_display(leftovers: Dict[str, Any]) -> Dict[str, Any]:
        """Format leftover data for frontend display"""
        
        return {
            'summary': leftovers['summary'],
            'batches': list(leftovers['batch_breakdown'].values()),
            'warnings': LeftoverCalculator._generate_warnings(leftovers)
        }
    
    @staticmethod
    def _generate_warnings(leftovers: Dict[str, Any]) -> List[str]:
        """Generate warnings based on allocation"""
        
        warnings = []
        summary = leftovers['summary']
        
        if summary['allocation_status'] == 'incomplete':
            warnings.append(
                f"⚠️  {summary['overall_leftover']} students could not be allocated"
            )
        
        if summary['capacity_utilization'] < 50:
            warnings.append(
                f"📊 Low capacity utilization: {summary['capacity_utilization']:.1f}%"
            )
        
        for batch_id, batch_info in leftovers['batch_breakdown'].items():
            if batch_info['leftover'] > 0:
                warnings.append(
                    f"Batch {batch_id}: {batch_info['leftover']} students unallocated"
                )
        
        return warnings