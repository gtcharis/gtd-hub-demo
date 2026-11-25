
import { useEffect, useMemo, useState } from "react";
import type { FormEvent } from "react";
import {
  ArrowUpRight,
  BookOpen,
  Download,
  FileText,
  Link2,
  Plus,
  Search,
  ShieldCheck,
  Upload,
  X,
  Pencil,
  Trash2,
} from "lucide-react";

import {
  api,
  type LearningCategory,
  type LearningResource,
} from "../../services/api";

import { useAuth } from "../auth/AuthContext";

type Draft = {
  title: string;
  description: string;
  category_id: string;
  resource_type: string;
  source_type: "upload" | "external_link";
  publisher: string;
  keywords: string;
  external_url: string;
  institution_id: string;
  file: File | null;
};

const emptyDraft: Draft = {
  title: "",
  description: "",
  category_id: "",
  resource_type: "Guide",
  source_type: "upload",
  publisher: "",
  keywords: "",
  external_url: "",
  institution_id: "",
  file: null,
};

const formatSize = (n: number | null) =>
  n == null
    ? "External resource"
    : n < 1024 * 1024
      ? `${Math.max(1, Math.round(n / 1024))} KB`
      : `${(n / (1024 * 1024)).toFixed(1)} MB`;

export default function LearningPage() {
  const { user } = useAuth();

  const canManage =
    user?.role === "Programme Administrator" ||
    user?.role === "Organisation Administrator";

  const [categories, setCategories] = useState<LearningCategory[]>([]);
  const [resources, setResources] = useState<LearningResource[]>([]);
  const [managed, setManaged] = useState<LearningResource[]>([]);

  const [institutions, setInstitutions] = useState<
    Array<{ id: number; name: string; code: string }>
  >([]);

  const [category, setCategory] = useState("all");
  const [query, setQuery] = useState("");

  const [draft, setDraft] = useState<Draft>(emptyDraft);
  const [editingId, setEditingId] = useState<number | null>(null);

  const [showForm, setShowForm] = useState(false);
  const [busy, setBusy] = useState(false);
  const [deletingId, setDeletingId] = useState<number | null>(null);

  const [error, setError] = useState("");
  const [notice, setNotice] = useState("");

  const [refreshKey, setRefreshKey] = useState(0);

  // Load institutions for Programme Administrators.
  useEffect(() => {
    if (user?.role === "Programme Administrator") {
      api
        .institutions()
        .then(setInstitutions)
        .catch(() => setInstitutions([]));
    }
  }, [user?.role]);

  // Load catalogue and management resources.
  useEffect(() => {
    let alive = true;

    Promise.all([
      api.learningCategories(),
      api.learningResources(
        query,
        category === "all" ? undefined : Number(category),
      ),
      canManage
        ? api.learningManageResources()
        : Promise.resolve([] as LearningResource[]),
    ])
      .then(([cats, rows, adminRows]) => {
        if (alive) {
          setCategories(cats);
          setResources(rows);
          setManaged(adminRows);
        }
      })
      .catch((e) => {
        if (alive) {
          setError(e.message || "The Learning Library could not be loaded.");
        }
      });

    return () => {
      alive = false;
    };
  }, [query, category, canManage, refreshKey]);

  const visible = useMemo(() => resources, [resources]);

  // Create or update a resource.
  const submit = async (event: FormEvent) => {
    event.preventDefault();

    setBusy(true);
    setError("");
    setNotice("");

    try {
      if (editingId !== null) {
        await api.updateLearningResource(editingId, {
          title: draft.title.trim(),
          description: draft.description,
          category_id: Number(draft.category_id),
          resource_type: draft.resource_type,
          publisher: draft.publisher,
          keywords: draft.keywords,
        });

        setNotice("Resource details updated successfully.");
      } else {
        await api.createLearningResource({
          ...draft,
          title: draft.title.trim(),
          category_id: Number(draft.category_id),
        });

        setNotice(
          "Resource saved as a draft. Publish it when it is ready for users.",
        );
      }

      setDraft(emptyDraft);
      setEditingId(null);
      setShowForm(false);
      setRefreshKey((v) => v + 1);
    } catch (e: any) {
      setError(e.message || "Resource could not be saved.");
    } finally {
      setBusy(false);
    }
  };

  // Open a published document or external resource.
  const access = async (resource: LearningResource) => {
    const tab = window.open("about:blank", "_blank");

    if (tab) {
      tab.opener = null;
    }

    try {
      const result = await api.accessLearningResource(resource.id);

      if (tab) {
        tab.location.href = result.url;
      } else {
        window.location.assign(result.url);
      }
    } catch (e: any) {
      tab?.close();
      setError(e.message || "Resource could not be opened.");
    }
  };

  // Populate the form for editing.
  const editResource = (resource: LearningResource) => {
    setEditingId(resource.id);

    setDraft({
      title: resource.title,
      description: resource.description || "",
      category_id: String(resource.category_id),
      resource_type: resource.resource_type,
      source_type: resource.source_type,
      publisher: resource.publisher || "",
      keywords: resource.keywords || "",
      external_url: resource.external_url || "",
      institution_id: resource.institution_id
        ? String(resource.institution_id)
        : "",
      file: null,
    });

    setShowForm(true);
    setError("");
    setNotice("");

    window.scrollTo({
      top: 0,
      behavior: "smooth",
    });
  };

  // Close the form and reset its state.
  const closeForm = () => {
    setShowForm(false);
    setEditingId(null);
    setDraft(emptyDraft);
    setError("");
  };

  // Publish, unpublish or archive.
  const action = async (
    id: number,
    name: "publish" | "unpublish" | "archive",
  ) => {
    setError("");
    setNotice("");

    try {
      await api.learningResourceAction(id, name);

      setNotice(
        `Resource ${
          name === "archive"
            ? "archived"
            : name === "publish"
              ? "published"
              : "unpublished"
        } successfully.`,
      );

      setRefreshKey((v) => v + 1);
    } catch (e: any) {
      setError(e.message || "The resource could not be updated.");
    }
  };

  // Permanently delete a resource.
  const deleteResource = async (resource: LearningResource) => {
    const confirmed = window.confirm(
      `Permanently delete "${resource.title}"?\n\n` +
        "This will remove the resource and its uploaded document, if applicable. " +
        "This action cannot be undone.",
    );

    if (!confirmed) return;

    setDeletingId(resource.id);
    setError("");
    setNotice("");

    try {
      await api.deleteLearningResource(resource.id);

      setNotice(`"${resource.title}" was permanently deleted.`);
      setRefreshKey((v) => v + 1);
    } catch (e: any) {
      setError(e.message || "The resource could not be deleted.");
    } finally {
      setDeletingId(null);
    }
  };

  return (
    <div className="learning-page">
      <header className="page-heading learning-heading">
        <div>
          <span className="eyebrow">LEARNING & ADVOCACY</span>

          <h1>Learning Library</h1>

          <p>
            Explore practical resources, learning materials and tools for
            gender-transformative change across STEM.
          </p>
        </div>

        {canManage && (
          <button
            className="primary-button"
            onClick={() => {
              if (showForm) {
                closeForm();
              } else {
                setEditingId(null);
                setDraft(emptyDraft);
                setShowForm(true);
              }
            }}
          >
            <Plus size={17} />
            Add resource
          </button>
        )}
      </header>

      <div className="learning-safeguard">
        <ShieldCheck size={18} />

        <span>
          Use approved programme and learning materials only. Do not upload case
          records, participant disclosures or identifiable safeguarding
          information.
        </span>
      </div>

      {error && (
        <div className="learning-alert error" role="alert">
          {error}
        </div>
      )}

      {notice && (
        <div className="learning-alert" role="status">
          {notice}
        </div>
      )}

      {/* Resource creation and editing form */}
      {showForm && canManage && (
        <form className="learning-form" onSubmit={submit}>
          <div className="learning-form-head">
            <div>
              <h2>
                {editingId !== null
                  ? "Edit learning resource"
                  : "Add a learning resource"}
              </h2>

              <p>
                {editingId !== null
                  ? "Update the resource information below."
                  : "New resources are saved as drafts until published."}
              </p>
            </div>

            <button
              type="button"
              className="icon-button"
              aria-label="Close"
              onClick={closeForm}
            >
              <X size={18} />
            </button>
          </div>

          <div className="learning-form-grid">
            {user?.role === "Programme Administrator" && (
              <label>
                Audience / institution
                <select
                  value={draft.institution_id}
                  disabled={editingId !== null}
                  onChange={(e) =>
                    setDraft({
                      ...draft,
                      institution_id: e.target.value,
                    })
                  }
                >
                  <option value="">Programme-wide</option>

                  {institutions.map((i) => (
                    <option key={i.id} value={i.id}>
                      {i.name}
                    </option>
                  ))}
                </select>
              </label>
            )}

            <label>
              Title
              <input
                required
                maxLength={180}
                value={draft.title}
                onChange={(e) =>
                  setDraft({
                    ...draft,
                    title: e.target.value,
                  })
                }
              />
            </label>

            <label>
              Category
              <select
                required
                value={draft.category_id}
                onChange={(e) =>
                  setDraft({
                    ...draft,
                    category_id: e.target.value,
                  })
                }
              >
                <option value="">Select category</option>

                {categories.map((c) => (
                  <option key={c.id} value={c.id}>
                    {c.name}
                  </option>
                ))}
              </select>
            </label>

            <label>
              Resource type
              <select
                value={draft.resource_type}
                onChange={(e) =>
                  setDraft({
                    ...draft,
                    resource_type: e.target.value,
                  })
                }
              >
                <option>Guide</option>
                <option>Toolkit</option>
                <option>Learning module</option>
                <option>Research</option>
                <option>Policy</option>
                <option>Video</option>
                <option>Other</option>
              </select>
            </label>

            <label>
              Publisher / organisation
              <input
                maxLength={180}
                value={draft.publisher}
                onChange={(e) =>
                  setDraft({
                    ...draft,
                    publisher: e.target.value,
                  })
                }
              />
            </label>

            <label className="wide">
              Description
              <textarea
                maxLength={1600}
                rows={3}
                value={draft.description}
                onChange={(e) =>
                  setDraft({
                    ...draft,
                    description: e.target.value,
                  })
                }
              />
            </label>

            <label className="wide">
              Keywords
              <input
                maxLength={500}
                placeholder="e.g. mentorship, gender equality, STEM"
                value={draft.keywords}
                onChange={(e) =>
                  setDraft({
                    ...draft,
                    keywords: e.target.value,
                  })
                }
              />
            </label>

            {editingId === null && (
              <>
                <label>
                  Resource source
                  <select
                    value={draft.source_type}
                    onChange={(e) =>
                      setDraft({
                        ...draft,
                        source_type: e.target.value as Draft["source_type"],
                        file: null,
                        external_url: "",
                      })
                    }
                  >
                    <option value="upload">Upload document</option>
                    <option value="external_link">External HTTPS link</option>
                  </select>
                </label>

                {draft.source_type === "upload" ? (
                  <label>
                    Document (PDF, DOCX, PPTX; max 10 MB)
                    <input
                      required
                      type="file"
                      accept=".pdf,.docx,.pptx,application/pdf,application/vnd.openxmlformats-officedocument.wordprocessingml.document,application/vnd.openxmlformats-officedocument.presentationml.presentation"
                      onChange={(e) =>
                        setDraft({
                          ...draft,
                          file: e.target.files?.[0] || null,
                        })
                      }
                    />
                  </label>
                ) : (
                  <label>
                    External HTTPS URL
                    <input
                      required
                      type="url"
                      placeholder="https://..."
                      value={draft.external_url}
                      onChange={(e) =>
                        setDraft({
                          ...draft,
                          external_url: e.target.value,
                        })
                      }
                    />
                  </label>
                )}
              </>
            )}

            {editingId !== null && (
              <p className="wide">
                The existing document or external link is retained. Changing
                the underlying file is not part of this edit operation.
              </p>
            )}
          </div>

          <div className="learning-form-actions">
            <button
              type="button"
              className="outline-button"
              onClick={closeForm}
            >
              Cancel
            </button>

            <button className="primary-button" disabled={busy}>
              {busy ? (
                "Saving…"
              ) : (
                <>
                  <Upload size={16} />
                  {editingId !== null ? "Save changes" : "Save draft"}
                </>
              )}
            </button>
          </div>
        </form>
      )}

      {/* Search and category filter */}
      <div className="learning-toolbar">
        <label className="learning-search">
          <Search size={17} />

          <input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Search resources, topics and keywords"
          />
        </label>

        <select
          aria-label="Filter by category"
          value={category}
          onChange={(e) => setCategory(e.target.value)}
        >
          <option value="all">All categories</option>

          {categories.map((c) => (
            <option key={c.id} value={c.id}>
              {c.name}
            </option>
          ))}
        </select>
      </div>

      {/* Published resource catalogue */}
      {visible.length ? (
        <div className="learning-resource-grid">
          {visible.map((resource) => (
            <article className="learning-resource-card" key={resource.id}>
              <div className="learning-resource-icon">
                {resource.source_type === "upload" ? (
                  <FileText size={26} />
                ) : (
                  <Link2 size={26} />
                )}

                <span>{resource.resource_type}</span>
              </div>

              <div className="learning-resource-content">
                <span className="eyebrow">{resource.category}</span>

                <h3>{resource.title}</h3>

                <p>{resource.description || "No description provided."}</p>

                <div className="learning-resource-meta">
                  <span>
                    {resource.publisher || resource.institution_name}
                  </span>

                  <span>{formatSize(resource.file_size)}</span>
                </div>

                <button
                  className="text-action"
                  onClick={() => access(resource)}
                >
                  {resource.source_type === "upload" ? (
                    <>
                      <Download size={15} />
                      Open document
                    </>
                  ) : (
                    <>
                      Open external resource
                      <ArrowUpRight size={15} />
                    </>
                  )}
                </button>
              </div>
            </article>
          ))}
        </div>
      ) : (
        <div className="learning-empty">
          <BookOpen size={32} />

          <h3>No published resources yet</h3>

          <p>
            There are currently no resources matching this search. Check
            another category or try a different search.
          </p>
        </div>
      )}

      {/* Administrator resource management */}
      {canManage && (
        <section className="learning-manage">
          <div className="learning-manage-heading">
            <div>
              <span className="eyebrow">RESOURCE ADMINISTRATION</span>
              <h2>Manage resources</h2>
            </div>

            <span>{managed.length} resources</span>
          </div>

          {managed.length ? (
            <div className="learning-manage-list">
              {managed.map((r) => (
                <div className="learning-manage-row" key={r.id}>
                  <div>
                    <strong>{r.title}</strong>

                    <small>
                      {r.category} · {r.status} · {r.institution_name}
                    </small>
                  </div>

                  <div className="learning-manage-actions">
                    <button
                      type="button"
                      onClick={() => editResource(r)}
                    >
                      <Pencil size={14} />
                      Edit
                    </button>

                    {r.status === "published" ? (
                      <button
                        type="button"
                        onClick={() => action(r.id, "unpublish")}
                      >
                        Unpublish
                      </button>
                    ) : r.status === "draft" ? (
                      <button
                        type="button"
                        onClick={() => action(r.id, "publish")}
                      >
                        Publish
                      </button>
                    ) : null}

                    {r.status !== "archived" && (
                      <button
                        type="button"
                        onClick={() => action(r.id, "archive")}
                      >
                        Archive
                      </button>
                    )}

                    <button
                      type="button"
                      className="learning-delete-button"
                      disabled={deletingId === r.id}
                      onClick={() => deleteResource(r)}
                    >
                      <Trash2 size={14} />
                      {deletingId === r.id ? "Deleting…" : "Delete"}
                    </button>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="learning-empty-small">
              No resources have been added yet.
            </p>
          )}
        </section>
      )}
    </div>
  );
}
