
#include "sygusparser_lexer.hh"
#include "sygusparser.y.hh"
#include "tree.h"

#include <cassert>
#include <map>
#include <unordered_map>

#include <boost/format.hpp>
#include <sstream>

typedef sort_element::sort_elements smt_sort;

class smt_expr
{
public:
    smt_sort sort;
    std::string name;
    long value;

    enum sort_expr_type
    {
        literal,
        func,
        let
    } type;

    std::vector<std::pair<std::string, smt_expr>> lets;
    std::vector<smt_expr> childs;
};

class smt_func_determine
{
public:
    std::string name;
    std::vector<smt_sort> params;

    bool operator==(const smt_func_determine &r) const
    {
        if (name != r.name || params.size() != r.params.size())
            return false;
        for (int i = 0; i < (int)params.size(); ++i)
            if (params[i] != r.params[i])
                return false;
        return true;
    }

    bool operator<(const smt_func_determine &r) const
    {
        if (name < r.name)
            return true;
        if (name > r.name)
            return false;

        if (params.size() < r.params.size())
            return true;
        if (params.size() > r.params.size())
            return false;

        for (int i = 0; i < (int)params.size(); ++i)
        {
            if (params[i] < r.params[i])
                return true;
            if (params[i] > r.params[i])
                return false;
        }

        return false;
    }

    std::string to_string() const
    {
        std::stringstream ss;
        ss << name;
        ss << "(";
        for (int i = 0; i < (int)params.size(); ++i)
        {
            if (i != 0)
                ss << ", ";
            ss << (params[i] == smt_sort::Bool) ? "Bool" : "Int";
        }
        ss << ")";
        return ss.str();
    }
};

class smt_func_determine_name : public smt_func_determine
{
public:
    std::vector<std::string> names;
};

class smt_funcdecl
{
public:
    smt_func_determine det;
    smt_sort result_sort;
};

class smt_funcdef
{
public:
    smt_func_determine_name det;
    smt_sort result_sort;
    smt_expr expression;

    bool internal = false;
};

class smt_synfun
{
    smt_func_determine_name det;
    smt_sort result_sort;
    std::map<std::string, std::vector<smt_expr>> rules;
};

class smt_solver
{
public:
    std::map<std::string, smt_sort> sort_table;
    std::map<smt_func_determine, smt_funcdef> defines;
    std::map<smt_func_determine, smt_funcdecl> decls;
    std::map<smt_func_determine, smt_synfun> synths;

    void solve(const sygus_command_list &cmds);

    void add_sort(const std::string &name, const smt_sort &val)
    {
        auto it = sort_table.find(name);
        if (it == sort_table.end())
        {
            sort_table.emplace(name, val);
        }
        else
        {
            throw std::runtime_error((boost::format("Sort already exists: '%1%'") % name).str());
        }
    }
    const smt_sort &get_sort(const std::string &name) const
    {
        auto it = sort_table.find(name);
        if (it == sort_table.end())
            throw std::runtime_error((boost::format("Unknown type name: '%1%'") % name).str());
        return it->second;
    }

    bool find_func(const smt_func_determine &det)
    {
        return defines.find(det) != defines.end() || decls.find(det) != decls.end() || synths.find(det) != synths.end();
    }

    bool ensure_func_not(const smt_func_determine &det)
    {
        if (find_func(det))
        {
            throw std::runtime_error((boost::format("Func already exists: '%1%'") % det.to_string()).str());
        }
    }

    smt_sort to_sort(std::shared_ptr<sort> sort_val) const
    {
        if (auto *s = dynamic_cast<sort_element *>(&*sort_val))
        {
            return s->get_sort();
        }
        else if (auto *s = dynamic_cast<sort_symbol *>(&*sort_val))
        {
            return get_sort(s->get_name());
        }
        else
        {
            throw std::runtime_error("Unknown sort type");
        }
    }

    smt_expr to_expr(std::shared_ptr<term> term) const;

    smt_sort get_return_sort() const
    {
        
    }
};

smt_expr smt_solver::to_expr(std::shared_ptr<term> term) const
{
    smt_expr result;

    if (auto t = dynamic_cast<term_func *>(&*term))
    {
        result.name = t->get_name();

    }
    else if (auto t = dynamic_cast<term_literal *>(&*term))
    {
    }
    else if (auto t = dynamic_cast<term_symbol *>(&*term))
    {
    }
    else if (auto t = dynamic_cast<term_let *>(&*term))
    {
    }
    else if (auto t = dynamic_cast<term_exp *>(&*term))
    {
    }
    else
    {
        throw std::runtime_error("Unknown term type");
    }

    return result;
}

void smt_solver::solve(const sygus_command_list &cmds)
{
    if (cmds.setlogic.get())
        if (!(cmds.setlogic->get_logic() == "LIA"))
            throw std::runtime_error("LIA is the only supported logic");

    for (auto cmd : cmds.cmds)
    {
        if (auto *c = dynamic_cast<cmd_define_sort *>(&*cmd))
        {
            add_sort(c->get_name(), to_sort(c->get_value()));
        }
        else if (auto *c = dynamic_cast<cmd_declare_var *>(&*cmd))
        {
            smt_func_determine det;
            det.name = c->get_name();
            ensure_func_not(det);
            smt_funcdecl decl;
            decl.det = det;
            decl.result_sort = to_sort(c->get_sort());
            decls.emplace(std::move(det), std::move(decl));
        }
        else if (auto *c = dynamic_cast<cmd_declare_fun *>(&*cmd))
        {
            smt_func_determine det;
            det.name = c->get_name();
            for (auto s : c->get_params())
                det.params.emplace_back(to_sort(s));
            ensure_func_not(det);
            smt_funcdecl decl;
            decl.det = det;
            decl.result_sort = to_sort(c->get_result());
            decls.emplace(std::move(det), std::move(decl));
        }
        else if (auto *c = dynamic_cast<cmd_define_fun *>(&*cmd))
        {
            smt_func_determine_name det;
            det.name = c->get_name();
            for (auto s : c->get_params())
                det.params.emplace_back(to_sort(s->get_sort()));
            ensure_func_not(det);
            for (auto s : c->get_params())
                det.names.emplace_back(s->get_name());
            smt_funcdef decl;
            decl.det = det;
            decl.result_sort = to_sort(c->get_result());
            // term to expression
            defines.emplace(std::move(det), std::move(decl));
        }
        else if (auto *c = dynamic_cast<cmd_synth_fun *>(&*cmd))
        {
        }
        else if (auto *c = dynamic_cast<cmd_constraint *>(&*cmd))
        {
        }
        else if (auto *c = dynamic_cast<cmd_check_synth *>(&*cmd))
        {
        }
        else if (auto *c = dynamic_cast<cmd_set_options *>(&*cmd))
        {
        }
        else
        {
            throw std::runtime_error("Unknown command type");
        }
    }
}

int main(int argc, char *argv[])
{
    sygus_command_list cmds;
    sygusparser::sygusparser_lexer lexer;
    sygusparser::parser parser{lexer, cmds};
    parser.parse();
    cmds.finish();

    std::cout << "finished\n";

    return 0;
}
