/** Copyright 2020 Alibaba Group Holding Limited.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 * 	http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

#ifndef ANALYTICAL_ENGINE_CORE_OBJECT_I_FRAGMENT_WRAPPER_H_
#define ANALYTICAL_ENGINE_CORE_OBJECT_I_FRAGMENT_WRAPPER_H_

#include <map>
#include <memory>
#include <string>
#include <utility>
#include <vector>

#include "vineyard/graph/utils/grape_utils.h"

#include "core/context/i_context.h"
#include "core/object/gs_object.h"
#include "core/server/rpc_utils.h"
#include "proto/attr_value.pb.h"
#include "proto/graph_def.pb.h"

namespace gs {
class IContextWrapper;

/**
 * @brief This is the base class of non-labeled fragment wrapper
 */
class IFragmentWrapper : public GSObject {
 public:
  explicit IFragmentWrapper(std::string id)
      : GSObject(std::move(id), ObjectType::kFragmentWrapper) {}

  virtual const rpc::graph::GraphDefPb& graph_def() const = 0;

  virtual std::shared_ptr<void> fragment() const = 0;

  virtual bl::result<std::shared_ptr<IFragmentWrapper>> CopyGraph(
      const grape::CommSpec& comm_spec, const std::string& dst_graph_name,
      const std::string& copy_type) = 0;

  virtual bl::result<std::string> ReportGraph(const grape::CommSpec& comm_spec,
                                              const rpc::GSParams& params) = 0;

  virtual bl::result<std::shared_ptr<IFragmentWrapper>> ToDirected(
      const grape::CommSpec& comm_spec, const std::string& dst_graph_name) = 0;

  virtual bl::result<std::shared_ptr<IFragmentWrapper>> ToUnDirected(
      const grape::CommSpec& comm_spec, const std::string& dst_graph_name) = 0;

  virtual bl::result<std::shared_ptr<IFragmentWrapper>> CreateGraphView(
      const grape::CommSpec& comm_spec, const std::string& dst_graph_name,
      const std::string& view_type) = 0;

 protected:
  explicit IFragmentWrapper(std::string id, ObjectType type)
      : GSObject(std::move(id), type) {}
};

/**
 * @brief This is the base class of labeled fragment wrapper
 */
class ILabeledFragmentWrapper : public IFragmentWrapper {
 public:
  explicit ILabeledFragmentWrapper(std::string id)
      : IFragmentWrapper(std::move(id), ObjectType::kLabeledFragmentWrapper) {}

  virtual bl::result<std::shared_ptr<ILabeledFragmentWrapper>> Project(
      const grape::CommSpec& comm_spec, const std::string& dst_graph_name,
      const std::map<int, std::vector<int>>& vertices,
      const std::map<int, std::vector<int>>& edges) = 0;

  virtual bl::result<std::shared_ptr<ILabeledFragmentWrapper>> AddColumn(
      const grape::CommSpec& comm_spec, const std::string& dst_graph_name,
      std::shared_ptr<IContextWrapper>& ctx_wrapper,
      const std::string& s_selectors) = 0;

  virtual bl::result<std::unique_ptr<grape::InArchive>> ToNdArray(
      const grape::CommSpec& comm_spec, const LabeledSelector& selector,
      const std::pair<std::string, std::string>& range) = 0;

  virtual bl::result<std::unique_ptr<grape::InArchive>> ToDataframe(
      const grape::CommSpec& comm_spec,
      const std::vector<std::pair<std::string, LabeledSelector>>& selectors,
      const std::pair<std::string, std::string>& range) = 0;
};
}  // namespace gs

#endif  // ANALYTICAL_ENGINE_CORE_OBJECT_I_FRAGMENT_WRAPPER_H_
