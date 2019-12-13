
#ifndef tree_header
#define tree_header

#include <string>
#include <vector>
#include <memory>
#include <algorithm>

#include <z3++.h>

class cmd
{
protected:
    cmd() = default;

public:
    virtual ~cmd() = default;
};

class cmd_set_logic : public cmd
{
public:
    virtual ~cmd_set_logic() = default;
    std::string logic;
    explicit cmd_set_logic(std::string s) : logic(s) {}
};

class cmd_define_sort : public cmd
{
public:
    virtual ~cmd_define_sort() = default;
    std::string name;
    z3::sort value;
    cmd_define_sort(const std::string &n, z3::sort v) : name(n), value(v) {}
};

class cmd_declare_var : public cmd
{
public:
    virtual ~cmd_declare_var() = default;
    std::string name;
    z3::sort s;
    cmd_declare_var(const std::string &n, z3::sort so) : name(n), s(so) {}
};

class cmd_declare_fun : public cmd
{
public:
    virtual ~cmd_declare_fun() = default;
    std::string name;
    z3::sort_vector params;
    z3::sort result;
    cmd_declare_fun(const std::string &n, z3::sort_vector p,
                    z3::sort r) : name(n), params(p), result(r) {}
};

class cmd_define_fun : public cmd
{
public:
    virtual ~cmd_define_fun() = default;
    z3::func_decl func;
    cmd_define_fun(z3::func_decl f) : func(f) {}
};

class synth_rule : public z3::object
{
public:
    virtual ~synth_rule() = default;
    std::string name;
    z3::sort s;
    z3::expr_vector rules;

    synth_rule(z3::context &ctx, const std::string &n, z3::sort so, const z3::expr_vector &r)
        : z3::object(ctx), name(n), s(so), rules(r) {}
};

class param : public z3::object
{
public:
    ~param() = default;
    std::string name;
    z3::sort s;

    param(z3::context &ctx, const std::string &n, z3::sort so) : z3::object(ctx), name(n), s(so) {}
};

class cmd_synth_fun : public cmd
{
public:
    virtual ~cmd_synth_fun() = default;
    std::string name;
    std::vector<param> params;
    z3::sort result;
    std::vector<synth_rule> body;
    cmd_synth_fun(const std::string &n, const std::vector<param> &p,
                  z3::sort r, std::vector<synth_rule> b) : name(n), params(p), result(r), body(b) {}
};

class cmd_constraint : public cmd
{
public:
    virtual ~cmd_constraint() = default;
    z3::expr t;
    cmd_constraint(z3::expr te) : t(te) {}
};

class cmd_check_synth : public cmd
{
public:
    virtual ~cmd_check_synth() = default;
    cmd_check_synth() = default;
};

class option : public z3::object
{
public:
    virtual ~option() = default;
    std::string name;
    std::string value;
    option(z3::context& ctx, const std::string &n, const std::string &v) :z3::object(ctx), name(n), value(v) {}
};

class cmd_set_options : public cmd
{
public:
    virtual ~cmd_set_options() = default;
    std::vector<option> options;
    cmd_set_options(const std::vector<option> &o) : options(o) {}
};

class string_wrap : public z3::object
{
public:
    virtual ~string_wrap() = default;
    std::string s;
    string_wrap(z3::context &ctx, const std::string &str) : z3::object(ctx), s(str) {}
};

template <typename T>
class list_wrap : public z3::object
{
public:
    virtual ~list_wrap() = default;
    std::vector<T> list;
    list_wrap(z3::context &ctx): z3::object(ctx) {}
};

class sygus_command_list
{
public:
    std::shared_ptr<cmd_set_logic> setlogic;
    std::vector<std::shared_ptr<cmd>> cmds;

    std::vector<z3::object*> objects;

    inline void add_cmd(std::shared_ptr<cmd> cmd)
    {
        cmds.push_back(cmd);
    }
    inline void add_set_logic(std::shared_ptr<cmd_set_logic> cmd)
    {
        setlogic = cmd;
    }
};

class node
{
    std::string str;
    
};

#endif
