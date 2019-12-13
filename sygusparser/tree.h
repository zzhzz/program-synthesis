
#ifndef tree_header
#define tree_header

#include <string>
#include <vector>
#include <memory>
#include <algorithm>
#include <iostream>

class object
{
public:
    virtual ~object() = default;

    virtual void output(std::ostream &s) const = 0;

protected:
    object() = default;
};

template <typename OST>
OST &operator<<(OST &s, const object &o)
{
    o.output(s);
    return s;
}

template <typename T>
inline std::shared_ptr<T> to_shared(T *v)
{
    return std::shared_ptr<T>(v);
}

template <typename T>
inline std::shared_ptr<T> to_shared_cast(object *v)
{
    return std::shared_ptr<T>(&dynamic_cast<T &>(*v));
}

class sort : public object
{
public:
    virtual ~sort() = default;

protected:
    sort() = default;
};

class sort_symbol : public sort
{
public:
    virtual ~sort_symbol() = default;

protected:
    std::string sort_name;

public:
    explicit sort_symbol(std::string s) : sort_name(s) {}
    const std::string &get_name() const { return sort_name; }

    virtual void output(std::ostream &s) const
    {
        s << sort_name;
    }
};

class sort_element : public sort
{
public:
    enum sort_elements
    {
        Int,
        Bool
    };

    virtual ~sort_element() = default;

protected:
    sort_elements sort_ele;

public:
    sort_element(sort_elements s) : sort_ele(s) {}
    sort_elements get_sort() const { return sort_ele; }

    virtual void output(std::ostream &s) const
    {
        switch (sort_ele)
        {
        case Int:
            s << "Int";
            break;
        case Bool:
            s << "Bool";
            break;
        }
    }
};

class term : public object
{
public:
    virtual ~term() = default;

protected:
    term() = default;
};

class term_func : public term
{
public:
    virtual ~term_func() = default;

protected:
    std::string name;
    std::vector<std::shared_ptr<term>> terms;

public:
    term_func(const std::string &n, const std::vector<std::shared_ptr<term>> &t) : name(n), terms(t) {}
    const std::string &get_name() const { return name; }
    const std::vector<std::shared_ptr<term>> &get_terms() const { return terms; }

    virtual void output(std::ostream &s) const
    {
        s << "( " << name << " ";
        for (auto t : terms)
        {
            t->output(s);
            s << " ";
        }
        s << ")";
    }
};

class term_literal : public term
{
public:
    virtual ~term_literal() = default;

protected:
    sort_element::sort_elements sort;
    long val;

public:
    term_literal(sort_element::sort_elements s, long v) : sort(s), val(v) {}
    sort_element::sort_elements get_sort() const { return sort; }
    long get_val() const { return val; }

    virtual void output(std::ostream &s) const
    {
        switch (sort)
        {
        case sort_element::Bool:
            s << (val ? "true" : "false");
            break;
        case sort_element::Int:
            s << val;
            break;
        }
    }
};

class term_symbol : public term
{
public:
    virtual ~term_symbol() = default;

protected:
    std::string sym;

public:
    term_symbol(const std::string s) : sym(s) {}
    const std::string &get_name() const { return sym; }
    virtual void output(std::ostream &s) const
    {
        s << sym;
    }
};

class let_term_item : public object
{
public:
    virtual ~let_term_item() = default;

protected:
    std::string name;
    std::shared_ptr<sort> s;
    std::shared_ptr<term> t;

public:
    let_term_item(const std::string &n, std::shared_ptr<sort> so, std::shared_ptr<term> te) : name(n), s(so), t(te) {}
    const std::string &get_name() const { return name; }
    std::shared_ptr<sort> get_sort() const { return s; }
    std::shared_ptr<term> get_term() const { return t; }

    virtual void output(std::ostream &s) const
    {
        s << "( " << name << " ";
        t->output(s);
        s << " )";
    }
};

class term_let : public term
{
public:
    virtual ~term_let() = default;

protected:
    std::vector<std::shared_ptr<let_term_item>> let_items;
    std::shared_ptr<term> t;

public:
    term_let(const std::vector<std::shared_ptr<let_term_item>> &let_i, std::shared_ptr<term> te) : let_items(let_i), t(te) {}
    const std::vector<std::shared_ptr<let_term_item>> &get_let_items() const { return let_items; }
    const std::shared_ptr<term> get_term() const { return t; }

    virtual void output(std::ostream &s) const
    {
        s << "( let (";
        for (auto i : let_items)
        {
            i->output(s);
            s << " ";
        }
        s << ") ";
        t->output(s);
        s << ")";
    }
};

class term_exp : public term
{
public:
    enum term_exp_type
    {
        Constant,
        Variable,
        InputVariable,
        LocalVariable
    };

    virtual ~term_exp() = default;

protected:
    term_exp_type t;
    std::shared_ptr<sort> s;

public:
    term_exp(term_exp_type type, std::shared_ptr<sort> so) : t(type), s(so) {}
    term_exp_type get_type() const { return t; }
    std::shared_ptr<sort> get_sort() const { return s; };

    virtual void output(std::ostream &s) const
    {
        s << "( ";
        switch (t)
        {
        case Constant:
            s << "Constant";
            break;
        case Variable:
            s << "Variable";
            break;
        case InputVariable:
            s << "InputVariable";
            break;
        case LocalVariable:
            s << "LocalVariable";
            break;
        }
        s << " ";
    }
};

class cmd : public object
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

protected:
    std::string logic;

public:
    explicit cmd_set_logic(std::string s) : logic(s) {}
    const std::string &get_logic() const { return logic; }

    virtual void output(std::ostream &s) const
    {
        s << "( set-logic " << logic << " )";
    }
};

class cmd_define_sort : public cmd
{
public:
    virtual ~cmd_define_sort() = default;

protected:
    std::string name;
    std::shared_ptr<sort> value;

public:
    cmd_define_sort(const std::string &n, std::shared_ptr<sort> v) : name(n), value(v) {}
    const std::string &get_name() const { return name; }
    std::shared_ptr<sort> get_value() const { return value; }

    virtual void output(std::ostream &s) const
    {
        s << "( define-sort " << name << " " << *value << " )";
    }
};

class cmd_declare_var : public cmd
{
public:
    virtual ~cmd_declare_var() = default;

protected:
    std::string name;
    std::shared_ptr<sort> s;

public:
    cmd_declare_var(const std::string &n, std::shared_ptr<sort> so) : name(n), s(so) {}
    const std::string &get_name() const { return name; }
    std::shared_ptr<sort> get_sort() const { return s; }

    virtual void output(std::ostream &s) const
    {
        s << "( declare-var " << name << " " << *this->s << " )";
    }
};

class cmd_declare_fun : public cmd
{
public:
    virtual ~cmd_declare_fun() = default;

protected:
    std::string name;
    std::vector<std::shared_ptr<sort>> params;
    std::shared_ptr<sort> result;

public:
    cmd_declare_fun(const std::string &n, const std::vector<std::shared_ptr<sort>> &p,
                    const std::shared_ptr<sort> r) : name(n), params(p), result(r) {}
    const std::string &get_name() const { return name; }
    const std::vector<std::shared_ptr<sort>> &get_params() const { return params; }
    std::shared_ptr<sort> get_result() const { return result; }

    virtual void output(std::ostream &s) const
    {
        s << "( declare-fun " << name << "( ";
        for (auto so : params)
            s << *so << " ";
        s << ") " << *result << ")";
    }
};

class param : public object
{
public:
    ~param() = default;

protected:
    std::string name;
    std::shared_ptr<sort> s;

public:
    param(const std::string &n, std::shared_ptr<sort> so) : name(n), s(so) {}
    const std::string &get_name() const { return name; }
    std::shared_ptr<sort> get_sort() const { return s; }

    virtual void output(std::ostream &s) const
    {
        s << "( " << name << " " << *this->s << " )";
    }
};

class cmd_define_fun : public cmd
{
public:
    virtual ~cmd_define_fun() = default;

protected:
    std::string name;
    std::vector<std::shared_ptr<param>> params;
    std::shared_ptr<sort> result;
    std::shared_ptr<term> body;

public:
    cmd_define_fun(const std::string &n, const std::vector<std::shared_ptr<param>> &p,
                   std::shared_ptr<sort> r, std::shared_ptr<term> b) : name(n), params(p), result(r), body(b) {}
    const std::string &get_name() const { return name; }
    const std::vector<std::shared_ptr<param>> &get_params() const { return params; }
    std::shared_ptr<sort> get_result() const { return result; }
    std::shared_ptr<term> get_body() const { return body; }

    virtual void output(std::ostream &s) const
    {
        s << "( define-fun " << name << "( ";
        for (auto p : params)
            s << *p << " ";
        s << ") " << result << " " << *body << ")";
    }
};

class synth_rule : public object
{
public:
    virtual ~synth_rule() = default;

protected:
    std::string name;
    std::shared_ptr<sort> s;
    std::vector<std::shared_ptr<term>> rules;

public:
    synth_rule(const std::string &n, std::shared_ptr<sort> so, const std::vector<std::shared_ptr<term>> &r) : name(n), s(so), rules(r) {}
    const std::string &get_name() const { return name; }
    std::shared_ptr<sort> get_sort() const { return s; }
    const std::vector<std::shared_ptr<term>> &get_rules() { return rules; }

    virtual void output(std::ostream &s) const
    {
        s << "( " << name << " " << *this->s << " ( ";
        for (auto r : rules)
            s << *r << " ";
        s << ") )";
    }
};

class cmd_synth_fun : public cmd
{
public:
    virtual ~cmd_synth_fun() = default;

protected:
    std::string name;
    std::vector<std::shared_ptr<param>> params;
    std::shared_ptr<sort> result;
    std::vector<std::shared_ptr<synth_rule>> body;

public:
    cmd_synth_fun(const std::string &n, const std::vector<std::shared_ptr<param>> &p,
                  std::shared_ptr<sort> r, std::vector<std::shared_ptr<synth_rule>> b) : name(n), params(p), result(r), body(b) {}
    const std::string &get_name() const { return name; }
    const std::vector<std::shared_ptr<param>> &get_params() const { return params; }
    std::shared_ptr<sort> get_result() const { return result; }
    const std::vector<std::shared_ptr<synth_rule>> &get_body() const { return body; }

    virtual void output(std::ostream &s) const
    {
        s << "( synth-fun " << name << " ( ";
        for (auto p : params)
            s << *p << " ";
        s << ") " << *result << " ( ";
        for (auto b : body)
            s << *b << " ";
        s << ") )";
    }
};

class cmd_constraint : public cmd
{
public:
    virtual ~cmd_constraint() = default;

protected:
    std::shared_ptr<term> t;

public:
    cmd_constraint(std::shared_ptr<term> te) : t(te) {}
    std::shared_ptr<term> get_term() const { return t; }

    virtual void output(std::ostream &s) const
    {
        s << "( constraint " << *t << " )";
    }
};

class cmd_check_synth : public cmd
{
public:
    virtual ~cmd_check_synth() = default;

    cmd_check_synth() = default;

    virtual void output(std::ostream &s) const
    {
        s << "( check-synth )";
    }
};

class option : public object
{
public:
    virtual ~option() = default;

protected:
    std::string name;
    std::string value;

public:
    option(const std::string &n, const std::string &v) : name(n), value(v) {}
    const std::string &get_name() const { return name; }
    const std::string &get_value() const { return value; }

    virtual void output(std::ostream &s) const
    {
        s << "( " << name << " " << value << " )";
    }
};

class cmd_set_options : public cmd
{
public:
    virtual ~cmd_set_options() = default;

protected:
    std::vector<std::shared_ptr<option>> options;

public:
    cmd_set_options(const std::vector<std::shared_ptr<option>> &o) : options(o) {}
    const std::vector<std::shared_ptr<option>> &get_options() const { return options; }

    virtual void output(std::ostream &s) const
    {
        s << "( set-options ( ";
        for (auto o : options)
            s << *o << " ";
        s << ") )";
    }
};

class string_wrap : public object
{
public:
    virtual ~string_wrap() = default;

protected:
    std::string s;

public:
    string_wrap(const std::string &str) : s(str) {}
    const std::string &get() const { return s; }

    virtual void output(std::ostream &s) const {}
};

template <typename T>
class list_wrap : public object
{
public:
    virtual ~list_wrap() = default;

protected:
    std::vector<std::shared_ptr<T>> list;

public:
    const std::vector<std::shared_ptr<T>> &get() const { return list; }
    void add(std::shared_ptr<T> p) { list.emplace_back(p); }
    void reverse() { std::reverse(list.begin(), list.end()); }
    std::vector<std::shared_ptr<T>> get()
    {
        return std::vector<std::shared_ptr<T>>(list.rbegin(), list.rend());
    }

    virtual void output(std::ostream &s) const {}
};

class sygus_command_list
{
public:
    std::shared_ptr<cmd_set_logic> setlogic;
    std::vector<std::shared_ptr<cmd>> cmds;

    inline void add_cmd(std::shared_ptr<cmd> cmd)
    {
        cmds.push_back(cmd);
    }
    inline void add_set_logic(std::shared_ptr<cmd_set_logic> cmd)
    {
        setlogic = cmd;
    }

    void finish()
    {
        std::reverse(cmds.begin(), cmds.end());
    }
};

#endif
