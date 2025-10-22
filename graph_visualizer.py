#!/usr/bin/env python3
"""
Graph Visualizer for COBOL Dependencies
Generates visual dependency graphs showing program relationships
"""

import networkx as nx
import matplotlib.pyplot as plt
from pathlib import Path
from typing import List, Dict, Set, Tuple
from dataclasses import dataclass


@dataclass
class GraphNode:
    """Represents a node in the dependency graph"""
    name: str
    node_type: str  # 'program', 'file', 'procedure'
    metadata: Dict = None
    
    def __post_init__(self):
        self.metadata = self.metadata or {}


class DependencyGraphGenerator:
    """Generates visual dependency graphs from COBOL analysis results"""
    
    def __init__(self, analyzers: List):
        """
        Args:
            analyzers: List of COBOLAnalyzer objects
        """
        self.analyzers = analyzers
        self.graph = nx.DiGraph()
        self.program_nodes = set()
        self.file_nodes = set()
        self.call_edges = []
        self.file_edges = []
    
    def build_graph(self):
        """Build the dependency graph from analysis results"""
        for analyzer in self.analyzers:
            info = analyzer.info
            program_id = info.program_id or info.file_name
            
            # Add program node
            self.program_nodes.add(program_id)
            self.graph.add_node(
                program_id,
                node_type='program',
                loc=info.lines_of_code,
                file=info.file_name
            )
            
            # Add CALL edges (program -> program)
            for called_program in info.calls:
                self.call_edges.append((program_id, called_program))
                self.graph.add_node(called_program, node_type='program')
                self.graph.add_edge(
                    program_id,
                    called_program,
                    edge_type='calls'
                )
            
            # Add file edges (program -> file)
            for file_name in info.files_used:
                self.file_nodes.add(file_name)
                self.file_edges.append((program_id, file_name))
                self.graph.add_node(file_name, node_type='file')
                self.graph.add_edge(
                    program_id,
                    file_name,
                    edge_type='uses'
                )
    
    def generate_visualization(self, output_path: str = "dependency_graph.png", 
                              style: str = "detailed"):
        """
        Generate and save dependency graph visualization
        
        Args:
            output_path: Path to save the image
            style: 'detailed', 'simple', or 'calls_only'
        """
        if not self.graph.nodes():
            self.build_graph()
        
        if style == "calls_only":
            self._generate_calls_only_graph(output_path)
        elif style == "simple":
            self._generate_simple_graph(output_path)
        else:
            self._generate_detailed_graph(output_path)
        
        return output_path
    
    def _generate_calls_only_graph(self, output_path: str):
        """Generate graph showing only program-to-program calls"""
        # Create subgraph with only program nodes
        program_graph = nx.DiGraph()
        for node in self.program_nodes:
            program_graph.add_node(node)
        
        for source, target in self.call_edges:
            program_graph.add_edge(source, target)
        
        if not program_graph.nodes():
            print("⚠️  No program calls found to visualize")
            return
        
        # Set up the plot
        plt.figure(figsize=(14, 10))
        plt.title("COBOL Program Call Dependencies", fontsize=16, fontweight='bold')
        
        # Layout
        if len(program_graph.nodes()) <= 10:
            pos = nx.spring_layout(program_graph, k=2, iterations=50)
        else:
            pos = nx.kamada_kawai_layout(program_graph)
        
        # Draw nodes
        nx.draw_networkx_nodes(
            program_graph, pos,
            node_color='#3498db',
            node_size=4000,
            node_shape='s',
            alpha=0.9
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            program_graph, pos,
            edge_color='#34495e',
            arrows=True,
            arrowsize=20,
            arrowstyle='->',
            width=2,
            alpha=0.6
        )
        
        # Draw labels
        nx.draw_networkx_labels(
            program_graph, pos,
            font_size=9,
            font_weight='bold',
            font_color='white'
        )
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ Call dependency graph saved: {output_path}")
    
    def _generate_simple_graph(self, output_path: str):
        """Generate simplified graph with basic styling"""
        if not self.graph.nodes():
            print("⚠️  No data to visualize")
            return
        
        plt.figure(figsize=(16, 12))
        plt.title("COBOL System Dependencies", fontsize=16, fontweight='bold')
        
        # Layout
        pos = nx.spring_layout(self.graph, k=3, iterations=50)
        
        # Separate nodes by type
        program_nodes = [n for n, d in self.graph.nodes(data=True) 
                        if d.get('node_type') == 'program']
        file_nodes = [n for n, d in self.graph.nodes(data=True) 
                     if d.get('node_type') == 'file']
        
        # Draw program nodes
        nx.draw_networkx_nodes(
            self.graph, pos,
            nodelist=program_nodes,
            node_color='#3498db',
            node_size=1500,
            node_shape='s',
            alpha=0.9,
            label='Programs'
        )
        
        # Draw file nodes
        nx.draw_networkx_nodes(
            self.graph, pos,
            nodelist=file_nodes,
            node_color='#e74c3c',
            node_size=1000,
            node_shape='o',
            alpha=0.9,
            label='Files'
        )
        
        # Draw edges
        nx.draw_networkx_edges(
            self.graph, pos,
            edge_color='#95a5a6',
            arrows=True,
            arrowsize=15,
            width=1.5,
            alpha=0.5
        )
        
        # Draw labels
        nx.draw_networkx_labels(
            self.graph, pos,
            font_size=8,
            font_weight='bold'
        )
        
        plt.legend(scatterpoints=1, loc='upper right', fontsize=12)
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ Simple dependency graph saved: {output_path}")
    
    def _generate_detailed_graph(self, output_path: str):
        """Generate detailed graph with colors, sizes, and legend"""
        if not self.graph.nodes():
            print("⚠️  No data to visualize")
            return
        
        plt.figure(figsize=(18, 14))
        
        # Create title with statistics
        num_programs = len(self.program_nodes)
        num_files = len(self.file_nodes)
        num_calls = len(self.call_edges)
        
        plt.suptitle(
            "COBOL System Dependency Graph",
            fontsize=18,
            fontweight='bold',
            y=0.98
        )
        plt.title(
            f"{num_programs} Programs • {num_files} Files • {num_calls} Call Dependencies",
            fontsize=12,
            pad=20
        )
        
        # Layout - choose based on graph size
        if len(self.graph.nodes()) <= 15:
            pos = nx.spring_layout(self.graph, k=3, iterations=100, seed=42)
        elif len(self.graph.nodes()) <= 30:
            pos = nx.kamada_kawai_layout(self.graph)
        else:
            pos = nx.spring_layout(self.graph, k=2, iterations=50, seed=42)
        
        # Separate nodes by type
        program_nodes = [n for n, d in self.graph.nodes(data=True) 
                        if d.get('node_type') == 'program']
        file_nodes = [n for n, d in self.graph.nodes(data=True) 
                     if d.get('node_type') == 'file']
        
        # Calculate node sizes based on LOC for programs
        node_sizes_programs = []
        for node in program_nodes:
            loc = self.graph.nodes[node].get('loc', 0)
            size = max(1000, min(3000, 1000 + loc * 2))  # Scale between 1000-3000
            node_sizes_programs.append(size)
        
        # Draw program nodes (squares)
        nx.draw_networkx_nodes(
            self.graph, pos,
            nodelist=program_nodes,
            node_color='#3498db',
            node_size=node_sizes_programs if node_sizes_programs else 2000,
            node_shape='s',
            alpha=0.9,
            edgecolors='#2c3e50',
            linewidths=2,
            label='Programs'
        )
        
        # Draw file nodes (circles)
        nx.draw_networkx_nodes(
            self.graph, pos,
            nodelist=file_nodes,
            node_color='#e74c3c',
            node_size=1200,
            node_shape='o',
            alpha=0.9,
            edgecolors='#c0392b',
            linewidths=2,
            label='Files'
        )
        
        # Separate edges by type
        call_edges = [(u, v) for u, v, d in self.graph.edges(data=True) 
                     if d.get('edge_type') == 'calls']
        file_edges = [(u, v) for u, v, d in self.graph.edges(data=True) 
                     if d.get('edge_type') == 'uses']
        
        # Draw call edges (program -> program)
        if call_edges:
            nx.draw_networkx_edges(
                self.graph, pos,
                edgelist=call_edges,
                edge_color='#2980b9',
                arrows=True,
                arrowsize=20,
                arrowstyle='->',
                width=2.5,
                alpha=0.7,
                label='Calls'
            )
        
        # Draw file edges (program -> file)
        if file_edges:
            nx.draw_networkx_edges(
                self.graph, pos,
                edgelist=file_edges,
                edge_color='#95a5a6',
                arrows=True,
                arrowsize=15,
                arrowstyle='->',
                width=1.5,
                alpha=0.4,
                style='dashed',
                label='Uses File'
            )
        
        # Draw labels with background
        labels = {}
        for node in self.graph.nodes():
            # Truncate long names
            label = str(node)
            if len(label) > 12:
                label = label[:10] + '..'
            labels[node] = label
        
        nx.draw_networkx_labels(
            self.graph, pos,
            labels=labels,
            font_size=8,
            font_weight='bold',
            font_color='white'
        )
        
        # Add legend
        plt.legend(
            scatterpoints=1,
            loc='upper left',
            fontsize=11,
            framealpha=0.9
        )
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor='white')
        plt.close()
        
        print(f"✅ Detailed dependency graph saved: {output_path}")
    
    def get_statistics(self) -> Dict:
        """Get graph statistics"""
        if not self.graph.nodes():
            self.build_graph()
        
        return {
            "total_nodes": len(self.graph.nodes()),
            "program_nodes": len(self.program_nodes),
            "file_nodes": len(self.file_nodes),
            "total_edges": len(self.graph.edges()),
            "call_edges": len(self.call_edges),
            "file_edges": len(self.file_edges),
            "isolated_programs": len(list(nx.isolates(self.graph))),
            "strongly_connected_components": nx.number_strongly_connected_components(self.graph)
        }
    
    def export_dot(self, output_path: str = "dependency_graph.dot"):
        """Export graph in DOT format for Graphviz"""
        if not self.graph.nodes():
            self.build_graph()
        
        nx.drawing.nx_pydot.write_dot(self.graph, output_path)
        print(f"✅ DOT file exported: {output_path}")
        print(f"   Generate image with: dot -Tpng {output_path} -o graph.png")
    
    def find_circular_dependencies(self) -> List[List[str]]:
        """Find circular dependencies in program calls"""
        if not self.graph.nodes():
            self.build_graph()
        
        # Create subgraph with only program nodes
        program_graph = nx.DiGraph()
        for node in self.program_nodes:
            program_graph.add_node(node)
        for source, target in self.call_edges:
            if source in self.program_nodes and target in self.program_nodes:
                program_graph.add_edge(source, target)
        
        # Find cycles
        try:
            cycles = list(nx.simple_cycles(program_graph))
            return cycles
        except:
            return []