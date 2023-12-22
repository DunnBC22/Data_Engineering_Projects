"""
#################################################################
#
#  Author: Brian Dunn
#
#  Approx. Date Completed: 11-25-2023
#
#  This is the class that defines the dictionary structure 
#  required for type hinting. This is used inside each of the 
#  subdag functions.
#    
#################################################################
"""

#################################################################
#
#  Import Necessary Libraries.
#
#################################################################


from __future__ import annotations

from typing import TypedDict
from datetime import timedelta


#################################################################
#
#  Create the sub-DAG for removing duplicate rows/samples.
#
#################################################################

class DAGConfig(TypedDict):
    owner: str
    retries: int
    retry_delay: timedelta