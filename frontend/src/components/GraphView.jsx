import React, { useEffect, useRef, useState, useMemo } from 'react';
import cytoscape from 'cytoscape';
import dagre from 'cytoscape-dagre';
import cola from 'cytoscape-cola';
import { ZoomIn, ZoomOut, Maximize2, ShieldAlert, Filter, RefreshCw, X } from 'lucide-react';

try {
  cytoscape.use(dagre);
  cytoscape.use(cola);
} catch (e) {
  // Ignore already registered
}

export default function GraphView({ graphData, highlightedChains, onNodeSelect, isDark = true }) {
  const containerRef = useRef(null);
  const cyRef = useRef(null);
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [activeLayout, setActiveLayout] = useState('cola'); // 'cola' (organic physics), 'concentric', 'dagre' (hierarchy DAG)
  const [threatOnly, setThreatOnly] = useState(false);
  const [selectedRepoFilter, setSelectedRepoFilter] = useState('all');

  // Compute unique repository list for filter dropdown
  const repoList = useMemo(() => {
    if (!graphData?.nodes) return [];
    return graphData.nodes
      .filter(n => n.data?.type === 'repository')
      .map(n => n.data?.label || n.data?.id)
      .sort();
  }, [graphData]);

  // Apply layout algorithm
  const runLayout = (layoutName, cyInstance) => {
    const cy = cyInstance || cyRef.current;
    if (!cy) return;

    let layoutConfig;
    if (layoutName === 'concentric') {
      layoutConfig = {
        name: 'concentric',
        fit: true,
        padding: 35,
        animate: true,
        animationDuration: 750,
        animationEasing: 'ease-in-out-cubic',
        avoidOverlap: true,
        nodeDimensionsIncludeLabels: true,
        minNodeSpacing: 30,
        spacingFactor: 1.25,
        concentric: (node) => {
          if (selectedNode) {
            if (node.data('id') === selectedNode.id || node.data('label') === selectedNode.label) {
              return 100;
            }
            const cyNode = cy.getElementById(node.data('id'));
            if (cyNode && cyNode.neighborhood(`[id = "${selectedNode.id}"]`).length > 0) {
              return 70;
            }
            if (cyNode && cyNode.neighborhood().neighborhood(`[id = "${selectedNode.id}"]`).length > 0) {
              return 45;
            }
            return 20;
          }
          const type = node.data('type');
          if (type === 'vulnerability') return 100;
          if (type === 'package') {
            const cyNode = cy.getElementById(node.data('id'));
            const hasCve = cyNode && cyNode.outgoers('edge[label="VULNERABLE_TO"]').length > 0;
            if (hasCve) return 75;
            const degree = cyNode ? cyNode.degree() : 1;
            if (degree > 2) return 55;
            return 35;
          }
          return 15;
        },
        levelWidth: () => 18
      };
    } else if (layoutName === 'dagre' || layoutName === 'breadthfirst' || layoutName === 'hierarchy') {
      // Directed Hierarchical Flow: Repositories at top, packages middle, CVEs bottom
      layoutConfig = {
        name: 'cola',
        animate: true,
        refresh: 1,
        maxSimulationTime: 2200,
        fit: true,
        padding: 35,
        randomize: false,
        avoidOverlap: true,
        nodeDimensionsIncludeLabels: true,
        nodeSpacing: () => 20,
        flow: { axis: 'y', minSeparation: 55 },
        edgeLength: (edge) => edge.data('label') === 'VULNERABLE_TO' ? 65 : 90,
        convergenceThreshold: 0.01
      };
    } else {
      // Balanced Organic Force-Directed Physics via WebCola
      layoutConfig = {
        name: 'cola',
        animate: true,
        refresh: 1,
        maxSimulationTime: 2000,
        fit: true,
        padding: 35,
        randomize: false,
        avoidOverlap: true,
        nodeDimensionsIncludeLabels: true,
        nodeSpacing: () => 22,
        edgeLength: (edge) => edge.data('label') === 'VULNERABLE_TO' ? 75 : 100,
        convergenceThreshold: 0.01
      };
    }

    try {
      const layout = cy.layout(layoutConfig);
      layout.one('layoutstop', () => {
        cy.resize();
        cy.fit(undefined, 35);
      });
      layout.run();
    } catch (err) {
      console.warn("Layout run error, falling back:", err);
      try {
        cy.layout({ name: 'cose', animate: false }).run();
        cy.resize();
        cy.fit(undefined, 35);
      } catch (e) {
        console.error("Fallback layout error:", e);
      }
    }
  };

  // Build Cytoscape stylesheet with clean adaptive badges & strict color constraints
  const getCytoscapeStyle = (darkMode) => [
    // Base Node Style - Dynamic auto-sized pills with ample breathing room so text NEVER overflows
    {
      selector: 'node',
      style: {
        'label': 'data(displayLabel)',
        'color': '#ffffff',
        'font-family': 'Inter, system-ui, -apple-system, sans-serif',
        'font-size': '11px',
        'font-weight': '600',
        'text-valign': 'center',
        'text-halign': 'center',
        'width': 'label',
        'height': 'label',
        'padding': '8px',
        'shape': 'round-rectangle',
        'corner-radius': '6px',
        'transition-property': 'background-color, border-color, width, height, opacity, transform',
        'transition-duration': '0.25s'
      }
    },
    // Repository Nodes - Solid Rich Warm Amber (STRICTLY the only yellow/amber element)
    {
      selector: 'node[type="repository"]',
      style: {
        'shape': 'round-rectangle',
        'corner-radius': '6px',
        'background-color': darkMode ? '#b45309' : '#d97706',
        'border-color': darkMode ? '#f59e0b' : '#92400e',
        'border-width': 1.5,
        'border-opacity': 0.85,
        'color': '#ffffff',
        'font-size': '11px',
        'font-weight': '700',
        'padding': '9px'
      }
    },
    // Package Nodes - Solid Cyber Emerald Pill
    {
      selector: 'node[type="package"]',
      style: {
        'shape': 'round-rectangle',
        'corner-radius': '12px',
        'background-color': darkMode ? '#047857' : '#059669',
        'border-color': darkMode ? '#10b981' : '#047857',
        'border-width': 1.5,
        'border-opacity': 0.8,
        'color': '#ffffff',
        'font-size': '10px',
        'font-weight': '600',
        'padding': '7px'
      }
    },
    // Vulnerability (CVE) Nodes - Solid Crimson Threat Badge
    {
      selector: 'node[type="vulnerability"]',
      style: {
        'shape': 'round-rectangle',
        'corner-radius': '4px',
        'background-color': darkMode ? '#be123c' : '#e11d48',
        'border-color': darkMode ? '#f43f5e' : '#9f1239',
        'border-width': 1.5,
        'border-opacity': 0.9,
        'color': '#ffffff',
        'font-size': '10px',
        'font-weight': '700',
        'padding': '7px'
      }
    },
    // Edge Styles - Crisp, balanced neutral connectors (Zero blue/violet)
    {
      selector: 'edge',
      style: {
        'width': 1.5,
        'line-color': darkMode ? '#52525b' : '#a1a1aa',
        'target-arrow-color': darkMode ? '#71717a' : '#71717a',
        'target-arrow-shape': 'triangle',
        'arrow-scale': 0.85,
        'curve-style': 'straight',
        'opacity': 0.75,
        'target-distance-from-node': 2,
        'source-distance-from-node': 2
      }
    },
    {
      selector: 'edge[label="VULNERABLE_TO"]',
      style: {
        'line-color': '#f43f5e',
        'target-arrow-color': '#f43f5e',
        'target-arrow-shape': 'triangle',
        'line-style': 'dashed',
        'line-dash-pattern': [5, 4],
        'width': 2,
        'opacity': 0.95
      }
    },
    // Highlighted States (Blast Radius Path)
    {
      selector: '.highlighted',
      style: {
        'border-color': '#ffffff',
        'border-width': 2.5,
        'background-color': '#e11d48',
        'color': '#ffffff',
        'z-index': 99
      }
    },
    {
      selector: '.highlighted-edge',
      style: {
        'line-color': '#f43f5e',
        'target-arrow-color': '#f43f5e',
        'width': 2.5,
        'opacity': 1.0,
        'z-index': 98
      }
    },
    {
      selector: '.dimmed',
      style: {
        'opacity': 0.15
      }
    }
  ];

  // Initialize Cytoscape
  useEffect(() => {
    if (!containerRef.current) return;

    const cy = cytoscape({
      container: containerRef.current,
      elements: [],
      boxSelectionEnabled: false,
      style: getCytoscapeStyle(isDark)
    });

    cy.on('tap', 'node', (evt) => {
      const node = evt.target;
      const data = node.data();
      setSelectedNode(data);
      if (onNodeSelect) onNodeSelect(data);

      cy.animate({
        center: { eles: node },
        zoom: Math.max(cy.zoom(), 1.15),
        duration: 350
      });
    });

    cy.on('mouseover', 'node', (evt) => {
      setHoveredNode(evt.target.data());
    });

    cy.on('mouseout', 'node', () => {
      setHoveredNode(null);
    });

    cy.on('tap', (evt) => {
      if (evt.target === cy) {
        setSelectedNode(null);
      }
    });

    cyRef.current = cy;

    // Observe container resizing to keep Cytoscape viewport in sync
    const ro = new ResizeObserver(() => {
      if (cyRef.current) {
        cyRef.current.resize();
      }
    });
    if (containerRef.current) {
      ro.observe(containerRef.current);
    }

    return () => {
      ro.disconnect();
      cy.destroy();
    };
  }, []);

  // Update Cytoscape style when dark mode changes
  useEffect(() => {
    if (!cyRef.current) return;
    cyRef.current.style(getCytoscapeStyle(isDark));
  }, [isDark]);

  // Sync elements when graphData, threatOnly, or selectedRepoFilter changes
  useEffect(() => {
    if (!cyRef.current || !graphData?.nodes) return;
    const cy = cyRef.current;

    let nodesToRender = [...graphData.nodes];
    let edgesToRender = [...(graphData.edges || [])];

    // Filter by selected repository if not 'all'
    if (selectedRepoFilter !== 'all') {
      const connectedNodeIds = new Set([selectedRepoFilter]);
      edgesToRender.forEach(edge => {
        if (edge.data?.source === selectedRepoFilter) {
          connectedNodeIds.add(edge.data.target);
        }
      });
      // Also grab transitive/CVEs attached to those packages
      edgesToRender.forEach(edge => {
        if (connectedNodeIds.has(edge.data?.source)) {
          connectedNodeIds.add(edge.data.target);
        }
      });

      nodesToRender = nodesToRender.filter(n => connectedNodeIds.has(n.data?.id));
      edgesToRender = edgesToRender.filter(
        e => connectedNodeIds.has(e.data?.source) && connectedNodeIds.has(e.data?.target)
      );
    }

    // Filter to threat paths only if enabled
    if (threatOnly) {
      const cveEdges = edgesToRender.filter(e => e.data?.label === 'VULNERABLE_TO');
      const vulnerablePkgIds = new Set(cveEdges.map(e => e.data?.source));
      const cveIds = new Set(cveEdges.map(e => e.data?.target));

      // Find repos and packages that depend on these vulnerable packages
      const threatRepoIds = new Set();
      edgesToRender.forEach(e => {
        if (vulnerablePkgIds.has(e.data?.target)) {
          threatRepoIds.add(e.data.source);
        }
      });

      const activeIds = new Set([...threatRepoIds, ...vulnerablePkgIds, ...cveIds]);
      nodesToRender = nodesToRender.filter(n => activeIds.has(n.data?.id));
      edgesToRender = edgesToRender.filter(
        e => activeIds.has(e.data?.source) && activeIds.has(e.data?.target)
      );
    }

    // Filter out completely orphaned nodes
    const activeEdgeNodeIds = new Set();
    edgesToRender.forEach(e => {
      if (e.data?.source) activeEdgeNodeIds.add(e.data.source);
      if (e.data?.target) activeEdgeNodeIds.add(e.data.target);
    });
    nodesToRender = nodesToRender.filter(n => activeEdgeNodeIds.has(n.data?.id));

    const preparedNodes = nodesToRender.map(n => {
      let displayLabel = n.data?.label || n.data?.id || '';
      if (n.data?.type === 'repository') {
        if (displayLabel.includes('/')) {
          displayLabel = displayLabel.split('/')[1];
        }
      } else if (n.data?.type === 'vulnerability') {
        if (displayLabel.startsWith('cve:')) displayLabel = displayLabel.slice(4);
      } else if (n.data?.type === 'package') {
        if (displayLabel.startsWith('pkg:')) displayLabel = displayLabel.slice(4);
      }
      return {
        ...n,
        data: {
          ...n.data,
          displayLabel
        }
      };
    });

    cy.batch(() => {
      cy.elements().remove();
      if (preparedNodes.length > 0) {
        cy.add(preparedNodes);
        cy.add(edgesToRender);
      }
    });

    runLayout(activeLayout, cy);
  }, [graphData, threatOnly, selectedRepoFilter]);

  // Sync highlighted blast chains
  useEffect(() => {
    if (!cyRef.current) return;
    const cy = cyRef.current;

    cy.batch(() => {
      cy.elements().removeClass('highlighted highlighted-edge dimmed');

      if (highlightedChains && highlightedChains.length > 0) {
        cy.elements().addClass('dimmed');

        highlightedChains.forEach(chain => {
          for (let i = 0; i < chain.length; i++) {
            const nodeName = chain[i];
            const node = cy.nodes().filter(n => {
              const d = n.data();
              return d.label === nodeName || d.displayLabel === nodeName || d.id === nodeName || d.id === `pkg:${nodeName}` || d.id === `cve:${nodeName}`;
            });
            if (node.length > 0) {
              node.removeClass('dimmed').addClass('highlighted');
            }

            if (i < chain.length - 1) {
              const nextNodeName = chain[i + 1];
              const edge = cy.edges().filter(e => {
                const s = e.source().data('label') || e.source().data('displayLabel');
                const t = e.target().data('label') || e.target().data('displayLabel');
                return (s === nodeName && t === nextNodeName) || (s === nextNodeName && t === nodeName);
              });
              edge.removeClass('dimmed').addClass('highlighted-edge');
            }
          }
        });
      }
    });
  }, [highlightedChains]);

  return (
    <div className="relative w-full h-full graph-grid-bg overflow-hidden flex flex-col select-none">
      {/* Top Controls Toolbar: Translucent Frosted Glass HUD */}
      <div className="absolute top-3 left-3 z-10 flex flex-wrap items-center gap-1.5 backdrop-blur-md bg-white/80 dark:bg-zinc-950/80 border border-zinc-200/80 dark:border-zinc-800/80 p-1.5 rounded-lg shadow-lg text-xs">
        {/* Layout Switcher */}
        <div className="flex items-center gap-0.5 bg-zinc-100/90 dark:bg-zinc-900/90 p-0.5 rounded-md border border-zinc-200/80 dark:border-zinc-800 font-medium">
          <button
            onClick={() => {
              setActiveLayout('cola');
              runLayout('cola');
            }}
            className={`px-2 py-1 rounded transition-colors ${
              activeLayout === 'cola' || activeLayout === 'cose'
                ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm font-semibold'
                : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
            }`}
          >
            Organic
          </button>
          <button
            onClick={() => {
              setActiveLayout('concentric');
              runLayout('concentric');
            }}
            className={`px-2 py-1 rounded transition-colors ${
              activeLayout === 'concentric'
                ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm font-semibold'
                : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
            }`}
          >
            Concentric
          </button>
          <button
            onClick={() => {
              setActiveLayout('dagre');
              runLayout('dagre');
            }}
            className={`px-2 py-1 rounded transition-colors ${
              activeLayout === 'dagre' || activeLayout === 'breadthfirst' || activeLayout === 'hierarchy'
                ? 'bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 shadow-sm font-semibold'
                : 'text-zinc-500 hover:text-zinc-800 dark:hover:text-zinc-200'
            }`}
          >
            Hierarchy
          </button>
        </div>

        {/* Separator */}
        <div className="h-4 w-[1px] bg-zinc-200 dark:bg-zinc-800 mx-0.5" />

        {/* Repository Focus Dropdown */}
        <div className="flex items-center gap-1 bg-zinc-100/90 dark:bg-zinc-900/90 px-2 py-1 rounded-md border border-zinc-200/80 dark:border-zinc-800 text-xs">
          <Filter className="w-3 h-3 text-zinc-500" />
          <select
            value={selectedRepoFilter}
            onChange={(e) => setSelectedRepoFilter(e.target.value)}
            className="bg-transparent text-zinc-700 dark:text-zinc-200 outline-none cursor-pointer font-medium text-xs pr-1"
          >
            <option value="all" className="bg-white dark:bg-zinc-900">All Services</option>
            {repoList.map(repo => (
              <option key={repo} value={repo} className="bg-white dark:bg-zinc-900">
                {repo}
              </option>
            ))}
          </select>
        </div>

        {/* Threat-Only Filter Toggle */}
        <button
          onClick={() => setThreatOnly(!threatOnly)}
          className={`flex items-center gap-1 px-2.5 py-1 rounded-md border text-xs font-medium transition-colors ${
            threatOnly
              ? 'bg-rose-50/90 dark:bg-rose-950/60 text-rose-700 dark:text-rose-400 border-rose-300 dark:border-rose-800 font-semibold'
              : 'bg-zinc-100/90 dark:bg-zinc-900/90 text-zinc-600 dark:text-zinc-400 border-zinc-200/80 dark:border-zinc-800 hover:text-zinc-900 dark:hover:text-zinc-200'
          }`}
        >
          <ShieldAlert className="w-3 h-3" />
          <span>Threats Only</span>
        </button>

        {/* Zoom & Fit Action Buttons */}
        <div className="flex items-center gap-0.5">
          <button
            onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 1.25)}
            className="p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-400"
            title="Zoom In"
          >
            <ZoomIn className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => cyRef.current?.zoom(cyRef.current.zoom() * 0.8)}
            className="p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-400"
            title="Zoom Out"
          >
            <ZoomOut className="w-3.5 h-3.5" />
          </button>
          <button
            onClick={() => cyRef.current?.fit(undefined, 40)}
            className="p-1.5 rounded-md hover:bg-zinc-100 dark:hover:bg-zinc-800 text-zinc-600 dark:text-zinc-400"
            title="Fit to Screen"
          >
            <Maximize2 className="w-3.5 h-3.5" />
          </button>
        </div>
      </div>

      {/* Live Hover Inspection Pill */}
      {hoveredNode && (
        <div className="absolute top-16 left-3 z-10 px-2.5 py-1.5 rounded-md text-[11px] font-mono backdrop-blur-md bg-white/90 dark:bg-zinc-950/90 text-zinc-900 dark:text-zinc-100 border border-zinc-200/80 dark:border-zinc-800/80 shadow-md pointer-events-none flex items-center gap-2 animate-in fade-in duration-150">
          <span
            className={`w-2.5 h-2.5 rounded-sm ${
              hoveredNode.type === 'repository'
                ? 'bg-amber-500'
                : hoveredNode.type === 'package'
                ? 'bg-emerald-500 rounded-full'
                : 'bg-rose-500 rotate-45'
            }`}
          />
          <span className="font-semibold">{hoveredNode.label || hoveredNode.id}</span>
          <span className="text-zinc-400 dark:text-zinc-500 text-[10px] uppercase font-sans">
            ({hoveredNode.type})
          </span>
          {hoveredNode.stars !== undefined && (
            <span className="text-zinc-500 font-sans text-[10px]">★ {hoveredNode.stars?.toLocaleString()}</span>
          )}
          {hoveredNode.severity && (
            <span className="text-rose-600 dark:text-rose-400 font-sans text-[10px] font-bold">
              {hoveredNode.severity} (CVSS {hoveredNode.cvss})
            </span>
          )}
        </div>
      )}

      {/* Empty / Loading State Overlay */}
      {(!graphData?.nodes || graphData.nodes.length === 0) && (
        <div className="absolute inset-0 z-20 flex flex-col items-center justify-center bg-white/80 dark:bg-zinc-950/80 backdrop-blur-xs text-zinc-600 dark:text-zinc-400">
          <RefreshCw className="w-6 h-6 animate-spin text-zinc-500 mb-2.5" />
          <span className="text-xs font-semibold text-zinc-800 dark:text-zinc-200">
            Synchronizing Graph Topology from Neo4j...
          </span>
          <span className="text-[11px] text-zinc-500 mt-1">
            Traversing dependency chains and vulnerabilities
          </span>
        </div>
      )}

      {/* Main Cytoscape Canvas */}
      <div id="cy-canvas" ref={containerRef} className="w-full h-full" />

      {/* Bottom Left Legend: Frosted Glass HUD */}
      <div className="absolute bottom-3 left-3 z-10 backdrop-blur-md bg-white/80 dark:bg-zinc-950/80 border border-zinc-200/80 dark:border-zinc-800/80 p-2.5 rounded-lg shadow-lg text-[11px] font-sans flex items-center gap-4">
        <div className="flex items-center gap-1.5">
          <span className="w-3.5 h-3.5 rounded bg-amber-500 border border-amber-600 inline-block shadow-sm" />
          <span className="font-medium text-zinc-700 dark:text-zinc-300">Repository</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3.5 h-3.5 rounded-full bg-emerald-500 border border-emerald-600 inline-block shadow-sm" />
          <span className="font-medium text-zinc-700 dark:text-zinc-300">Package</span>
        </div>
        <div className="flex items-center gap-1.5">
          <span className="w-3.5 h-3.5 rotate-45 bg-rose-500 border border-rose-600 inline-block shadow-sm" />
          <span className="font-medium text-zinc-700 dark:text-zinc-300">Vulnerability (CVE)</span>
        </div>
      </div>

      {/* Selected Node Details Drawer */}
      {selectedNode && (
        <div className="absolute bottom-3 right-3 z-10 backdrop-blur-md bg-white/95 dark:bg-zinc-950/95 border border-zinc-200 dark:border-zinc-800 p-3.5 rounded-lg shadow-2xl max-w-sm w-72 text-xs animate-in fade-in duration-200">
          <div className="flex items-start justify-between gap-2 mb-2 pb-2 border-b border-zinc-100 dark:border-zinc-800">
            <div>
              <span className="text-[10px] uppercase font-bold tracking-wider text-zinc-400 dark:text-zinc-500 block">
                {selectedNode.type}
              </span>
              <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 text-sm break-all">
                {selectedNode.label || selectedNode.id}
              </h3>
            </div>
            <button
              onClick={() => setSelectedNode(null)}
              className="text-zinc-400 hover:text-zinc-600 dark:hover:text-zinc-200 p-0.5 rounded"
            >
              <X className="w-3.5 h-3.5" />
            </button>
          </div>

          <div className="space-y-1.5 text-zinc-600 dark:text-zinc-300 text-[11px]">
            {selectedNode.type === 'repository' && (
              <>
                <div className="flex justify-between">
                  <span className="text-zinc-400">Language:</span>
                  <span className="font-medium">{selectedNode.language || 'Unknown'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-zinc-400">GitHub Stars:</span>
                  <span className="font-mono font-medium">{selectedNode.stars?.toLocaleString() || 0}</span>
                </div>
              </>
            )}

            {selectedNode.type === 'package' && (
              <>
                <div className="flex justify-between">
                  <span className="text-zinc-400">Ecosystem:</span>
                  <span className="font-medium">{selectedNode.ecosystem || 'npm'}</span>
                </div>
                <div className="mt-2 pt-2 border-t border-zinc-100 dark:border-zinc-800">
                  <button
                    onClick={() => onNodeSelect && onNodeSelect(selectedNode)}
                    className="w-full py-1.5 px-2 bg-zinc-900 hover:bg-zinc-800 dark:bg-zinc-100 dark:hover:bg-white text-white dark:text-zinc-900 font-semibold rounded text-xs transition-colors"
                  >
                    Query Blast Radius
                  </button>
                </div>
              </>
            )}

            {selectedNode.type === 'vulnerability' && (
              <>
                <div className="flex justify-between">
                  <span className="text-zinc-400">Severity:</span>
                  <span className="font-semibold text-rose-600 dark:text-rose-400 uppercase">
                    {selectedNode.severity} (CVSS {selectedNode.cvss})
                  </span>
                </div>
              </>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
