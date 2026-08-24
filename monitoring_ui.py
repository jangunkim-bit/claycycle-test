import streamlit as st

from interactive_monitoring import terminal_settlement_selection_figure


def _selection_signature(fit_results):
    return tuple((int(r["dataset"]), float(r["imax"])) for r in fit_results)


def selected_monitoring_index(fit_results):
    """Return active sorted-stage index; reset to true latest when datasets change."""
    if not fit_results:
        return None
    signature = _selection_signature(fit_results)
    if st.session_state.get("monitoring_selection_signature") != signature:
        st.session_state["monitoring_selection_signature"] = signature
        st.session_state["monitoring_selected_index"] = len(fit_results) - 1
    idx = int(st.session_state.get("monitoring_selected_index", len(fit_results) - 1))
    return max(0, min(idx, len(fit_results) - 1))


def active_monitoring_result(fit_results):
    idx = selected_monitoring_index(fit_results)
    return fit_results[idx] if idx is not None else None


def render_terminal_settlement_selector(fit_results, design_delta_st_mm):
    """Render clickable D-points and persist the selected monitoring stage."""
    idx = selected_monitoring_index(fit_results)
    event = st.plotly_chart(
        terminal_settlement_selection_figure(
            fit_results, design_delta_st_mm, selected_index=idx
        ),
        use_container_width=True,
        key="terminal_settlement_stage_selector",
        on_select="rerun",
        selection_mode="points",
    )
    st.caption(
        "Click any D-point to inspect that monitoring stage. The selected point, "
        "1% stability assessment, and Section 6 results update together."
    )

    try:
        points = event.selection.points
    except (AttributeError, TypeError):
        try:
            points = event.get("selection", {}).get("points", [])
        except AttributeError:
            points = []

    if not points:
        return fit_results[idx]

    try:
        point = dict(points[-1])
    except (TypeError, ValueError):
        point = points[-1]

    clicked_idx = None
    if hasattr(point, "get"):
        clicked_idx = point.get("customdata")
        if isinstance(clicked_idx, (list, tuple)) and clicked_idx:
            clicked_idx = clicked_idx[0]
        if clicked_idx is None and point.get("curve_number") == 1:
            clicked_idx = point.get("point_index")

    try:
        clicked_idx = int(clicked_idx)
    except (TypeError, ValueError):
        clicked_idx = None

    if (
        clicked_idx is not None
        and 0 <= clicked_idx < len(fit_results)
        and clicked_idx != idx
    ):
        st.session_state["monitoring_selected_index"] = clicked_idx
        st.rerun()

    return fit_results[idx]
